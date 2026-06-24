# На человеческий

Помощник для онбординга и взаимодействия в digital-командах.
Переводит сленговые фразы в понятный смысл, ожидаемое действие и профессиональный ответ.



## Что делает приложение

Пользователь вставляет фразу из рабочего чата, таски, созвона или письма.
Приложение объясняет:

- **Что это значит** — перевод на понятный язык
- **Термины** — разбор каждого сленгового слова
- **Что от вас хотят** — практическая интерпретация
- **Где можно ошибиться** — контекстные ловушки и двусмысленности
- **Как профессионально переспросить** — готовая формулировка

Поддерживаемые режимы: Смешанный, IT, Product, Marketing, E-commerce, Зумерский.

Приложение отправляет текст в backend, backend обращается к GPT, получает понятное объяснение, возвращает результат пользователю. и делает запись в историю (базу данных)


## Структура проекта
```
it-translator-Human/
|-- backend/
|   |-- __init__.py       # файл для Python-импортов
|   |-- main.py           # FastAPI: эндпоинты
|   |-- gpt_service.py    # интеграция с OpenAI API
|   |-- database.py       # SQLite: сохранение и чтение истории
|-- frontend/
|   |-- app.py            # Streamlit: веб-интерфейс
|-- requirements.txt      # зависимости Python
|-- .env.example          # пример переменных окружения без настоящего ключа
|-- .gitignore            # файлы, которые не загружаются на GitHub
|-- README.md             # описание проекта
```


## Схема работы

1. Streamlit frontend (frontend/app.py)

2. FastAPI backend (backend/main.py)

3. gpt_service.py -> OpenAI GPT

4. database.py -> SQLite (история переводов)

5. ответ пользователю




Backend доступен по адресу: `http://localhost:8000`

Документация API (Swagger): `http://localhost:8000/docs`

Frontend доступен по адресу: `http://localhost:8501`



## Переменные окружения  .env

 `OPENAI_API_KEY`  =  API-ключ OpenAI                          
 `OPENAI_BASE_URL` = `https://api.openai.com/v1`  =  Базовый URL OpenAI API 
 `OPENAI_MODEL`    = `gpt-4o`                     =  Модель GPT                        
 `DB_PATH`         = `translations.db`            =  Путь к файлу базы данных SQLite                      
 `BACKEND_URL`     = `http://localhost:8000`      =  Адрес backend для Streamlit-фронтенда           



## Не загружается на GitHub

В .gitignore добавлены файлы и папки:
   .env
   *.db
   .venv/
   venv/
   __pycache__/
   Human_venv

Чтобы не загрузить:
  - настоящий API-ключ
  - локальную базу данных
  - виртуальное окружение Python

Файл .env.example загружен на GitHub для примера



## Эндпоинты API

 GET   = `/health`                     = Проверка работоспособности backend          
 POST  = `/translate`                  = Перевести фразу на понятный язык      
 POST  = `/translate/simplify`         = Объяснить перевод проще                     
 POST  = `/translate/formulate-answer` = Сформулировать профессиональный ответ       
 GET   = `/history`                    = История переводов из базы данных SQLite       



## Технологии

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** Streamlit
- **AI:** OpenAI GPT (через официальный API)
- **База данных:** SQLite (история переводов)
