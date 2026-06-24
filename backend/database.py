import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "translations.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                mode        TEXT NOT NULL,
                translation TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)
        conn.commit()


def save_translation(original_text: str, mode: str, translation: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO translations
               (original_text, mode, translation, created_at)
               VALUES (?, ?, ?, ?)""",
            (original_text, mode, translation, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def get_history(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, original_text, mode, translation, created_at
               FROM translations
               ORDER BY id DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
