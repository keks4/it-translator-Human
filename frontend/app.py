import os

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

MODES = {
    "Смешанный": "mixed",
    "IT": "it",
    "Product": "product",
    "Marketing": "marketing",
    "E-commerce": "ecommerce",
    "Зумерский": "zoomer",
}

st.set_page_config(
    page_title="На человеческий",
    page_icon="💬",
    layout="centered",
)

st.title("На человеческий")
st.caption(
    "Помощник для онбординга и взаимодействия в digital-командах. "
    "Переводит сленговые фразы в понятный смысл, ожидаемое действие и профессиональный ответ."
)

tab_translate, tab_history = st.tabs(["Переводчик", "История"])

with tab_translate:
    mode_label = st.radio(
        "Режим",
        options=list(MODES.keys()),
        horizontal=True,
        index=0,
    )
    mode = MODES[mode_label]

    text = st.text_area(
        "Что перевести на человеческий?",
        placeholder='Например: «Давайте заскипаем этот флоу до апрува спеки, а креосы пока не пушим»',
        height=120,
        max_chars=1500,
    )

    col1, col2 = st.columns([1, 1])
    translate_btn = col1.button("Перевести", type="primary", use_container_width=True)
    clear_btn = col2.button("Очистить", use_container_width=True)

    if clear_btn:
        st.session_state.pop("result", None)
        st.session_state.pop("formulated_answer", None)
        st.rerun()

    if translate_btn:
        if not text.strip():
            st.warning("Введите текст для перевода.")
        else:
            with st.spinner("Переводим..."):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/translate",
                        json={"text": text, "mode": mode},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    st.session_state["result"] = resp.json()
                    st.session_state["original_text"] = text
                    st.session_state["mode"] = mode
                    st.session_state.pop("formulated_answer", None)
                except requests.exceptions.ConnectionError:
                    st.error("Не удалось подключиться к backend. Убедитесь, что сервер запущен.")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

    result = st.session_state.get("result")

    if result:
        if not result.get("isRelevant"):
            st.info(result.get("offTopicMessage", "Нерелевантный запрос."))
        else:
            st.subheader("Перевод")
            st.write(result.get("humanTranslation", ""))

            terms = result.get("terms") or []
            if terms:
                st.subheader("Термины")
                for t in terms:
                    st.markdown(f"**{t['term']}** — {t['meaning']}")

            if result.get("whatTheyProbablyWant"):
                st.subheader("Что от вас хотят")
                st.write(result["whatTheyProbablyWant"])

            if result.get("riskOfMisunderstanding"):
                st.subheader("Где можно ошибиться")
                st.write(result["riskOfMisunderstanding"])

            if result.get("professionalClarification"):
                st.subheader("Как профессионально переспросить")
                st.code(result["professionalClarification"], language=None)

            warning = result.get("internalTermWarning") or {}
            if warning.get("hasWarning"):
                st.warning(warning.get("message", "Возможен внутренний термин компании."))
                if warning.get("clarificationQuestion"):
                    st.info(warning["clarificationQuestion"])

            st.divider()
            col_s, col_f = st.columns(2)

            if col_s.button("Объяснить проще"):
                with st.spinner("Упрощаем..."):
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/translate/simplify",
                            json={
                                "original_text": st.session_state["original_text"],
                                "mode": st.session_state["mode"],
                                "previous_result": result,
                            },
                            timeout=60,
                        )
                        resp.raise_for_status()
                        st.session_state["result"] = resp.json()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

            if col_f.button("Сформулировать ответ"):
                with st.spinner("Формулируем ответ..."):
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/translate/formulate-answer",
                            json={
                                "original_text": st.session_state["original_text"],
                                "mode": st.session_state["mode"],
                                "translation_context": result.get("humanTranslation", ""),
                            },
                            timeout=60,
                        )
                        resp.raise_for_status()
                        st.session_state["formulated_answer"] = resp.json().get("answer", "")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

            formulated = st.session_state.get("formulated_answer")
            if formulated:
                st.subheader("Готовый ответ")
                st.success(f"«{formulated}»")

with tab_history:
    st.subheader("История переводов")
    if st.button("Обновить"):
        st.rerun()

    try:
        resp = requests.get(f"{BACKEND_URL}/history", timeout=10)
        resp.raise_for_status()
        records = resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к backend.")
        records = []
    except Exception as e:
        st.error(f"Ошибка: {e}")
        records = []

    if not records:
        st.info("История пустая. Сделайте первый перевод.")
    else:
        for rec in records:
            with st.expander(f"#{rec['id']} — {rec['original_text'][:60]}…  ({rec['created_at'][:16]})"):
                st.markdown(f"**Режим:** {rec['mode']}")
                st.markdown(f"**Оригинал:** {rec['original_text']}")
                st.markdown(f"**Перевод:** {rec['translation']}")
