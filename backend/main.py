from contextlib import asynccontextmanager
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from backend import database, gpt_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title="На человеческий — API",
    description="Переводчик профессионального и зумерского сленга на понятный язык.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ModeType = Literal["mixed", "it", "product", "marketing", "ecommerce", "zoomer"]


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1500)
    mode: ModeType = "mixed"


class SimplifyRequest(BaseModel):
    original_text: str
    mode: ModeType = "mixed"
    previous_result: dict[str, Any]


class FormulateRequest(BaseModel):
    original_text: str
    mode: ModeType = "mixed"
    translation_context: str


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.post("/translate", tags=["translate"])
def translate(body: TranslateRequest):
    try:
        result = gpt_service.translate(body.text, body.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI: {e}")

    if result.get("isRelevant"):
        try:
            database.save_translation(
                original_text=body.text,
                mode=body.mode,
                translation=result.get("humanTranslation", ""),
            )
        except Exception:
            pass

    return result


@app.post("/translate/simplify", tags=["translate"])
def simplify(body: SimplifyRequest):
    try:
        return gpt_service.simplify(body.original_text, body.mode, body.previous_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI: {e}")


@app.post("/translate/formulate-answer", tags=["translate"])
def formulate_answer(body: FormulateRequest):
    try:
        return gpt_service.formulate_answer(
            body.original_text, body.mode, body.translation_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI: {e}")


@app.get("/history", tags=["history"])
def history(limit: int = 20):
    try:
        return database.get_history(limit=min(limit, 100))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
