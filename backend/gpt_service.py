import json
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

SYSTEM_PROMPT = """Ты — AI-помощник продукта «На человеческий». 
Твоя задача — переводить IT, Product, Marketing, E-commerce / marketplace и зумерский сленг на понятный человеческий язык.

Пользователь вставляет фразу из рабочего чата, таски, созвона, письма, комментария или похожего контекста. 
Ты должен объяснить не только отдельные слова, но и общий смысл фразы, возможное ожидаемое действие пользователя и профессиональный способ переспросить.

Ты не универсальный чат-бот. Не выполняй нерелевантные задачи: не пиши стратегии, резюме, код, посты, исследования и т.д. 
Если запрос не про перевод/разбор рабочей или молодежной фразы, мягко верни пользователя к основной функции.

Всегда отвечай на русском языке и строго в формате JSON по следующей структуре:

Для релевантного запроса:
{
  "isRelevant": true,
  "humanTranslation": "краткий перевод всей фразы простым взрослым профессиональным языком",
  "terms": [
    { "term": "термин", "meaning": "объяснение" }
  ],
  "whatTheyProbablyWant": "практическая интерпретация ожидаемого действия",
  "riskOfMisunderstanding": "двусмысленности, многозначные слова, контекстные ловушки",
  "professionalClarification": "готовая формулировка вопроса для рабочего чата",
  "internalTermWarning": {
    "hasWarning": false,
    "message": null,
    "clarificationQuestion": null
  }
}

Для нерелевантного запроса:
{
  "isRelevant": false,
  "offTopicMessage": "Я помогаю переводить рабочий и молодежный сленг на понятный язык. Вставьте фразу из чата, таски, письма или созвона — и я разберу, что она значит, что от вас хотят и как профессионально переспросить."
}

Тон: спокойный, поддерживающий, профессиональный, без снобизма и без высмеивания. Объясняй так, чтобы взрослый профессионал без IT-бэкграунда быстро понял смысл. Не упрощай до детского уровня.

Если термин многозначный, укажи возможные значения и выбери наиболее вероятное по контексту. 
Если термин похож на внутренний жаргон компании, не придумывай точное значение: скажи, что это может быть внутренний термин, объясни остальную понятную часть фразы и предложи профессиональный уточняющий вопрос. 
В этом случае установи hasWarning: true в internalTermWarning.

Используй internalTermWarning только если слово действительно не похоже на общеизвестный термин или выглядит как внутреннее название процесса/команды/проекта.

Если пользователь выбрал режим, учитывай его:
- it: разработка, QA, DevOps, аналитика, API, баги, релизы, таски
- product: гипотезы, roadmap, discovery, CJM, фичи, метрики, приоритизация
- marketing: воронки, креативы, CAC, LTV, лиды, офферы, performance
- ecommerce: карточки товаров, SKU, остатки, фулфилмент, селлеры, CTR, SEO, акции
- zoomer: молодежный сленг, мемные выражения, тональность, уместность
- mixed: если фраза содержит термины из разных сфер

Возвращай ТОЛЬКО валидный JSON без markdown-обертки."""

FORMULATE_SYSTEM_PROMPT = (
    "Ты помогаешь профессионально ответить на рабочие сообщения. "
    "На основе оригинальной фразы и её разбора напиши готовый профессиональный ответ, "
    "который можно скопировать и отправить в рабочий чат. "
    "Ответ должен быть спокойным, деловым, уместным. "
    'Верни JSON: { "answer": "текст ответа" }. Только JSON без markdown.'
)

MODE_LABELS: dict[str, str] = {
    "mixed": "смешанный",
    "it": "IT",
    "product": "Product",
    "marketing": "Marketing",
    "ecommerce": "E-commerce / marketplace",
    "zoomer": "зумерский",
}


def _mode_label(mode: str) -> str:
    return MODE_LABELS.get(mode, "смешанный")


def translate(text: str, mode: str) -> dict:
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Режим: {_mode_label(mode)}\n\nФраза:\n{text}"},
        ],
    )
    raw = completion.choices[0].message.content or ""
    return json.loads(raw)


def simplify(original_text: str, mode: str, previous_result: dict) -> dict:
    prev_json = json.dumps(previous_result, ensure_ascii=False, indent=2)
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Режим: {_mode_label(mode)}\n\n"
                    f"Фраза:\n{original_text}\n\n"
                    f"Предыдущий разбор:\n{prev_json}\n\n"
                    "Пожалуйста, объясни то же самое проще — но не детским языком. "
                    "Сохрани ту же структуру JSON. "
                    "Аудитория — взрослый профессионал без технического бэкграунда."
                ),
            },
        ],
    )
    raw = completion.choices[0].message.content or ""
    return json.loads(raw)


def formulate_answer(original_text: str, mode: str, translation_context: str) -> dict:
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": FORMULATE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Режим: {_mode_label(mode)}\n\n"
                    f"Оригинальная фраза:\n{original_text}\n\n"
                    f"Контекст разбора:\n{translation_context}\n\n"
                    "Напиши профессиональный ответ на эту фразу."
                ),
            },
        ],
    )
    raw = completion.choices[0].message.content or ""
    return json.loads(raw)
