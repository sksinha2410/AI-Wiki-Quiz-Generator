from __future__ import annotations

import json
import os
from typing import Generator, List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, models
from .config import get_settings
from .database import SessionLocal, engine
from .llm import generate_quiz_payload
from .scraper import fetch_article

settings = get_settings()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/quiz")
def create_quiz(payload: dict, db: Session = Depends(get_db)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        article = fetch_article(url)
    except Exception as exc:  # pragma: no cover - network errors
        raise HTTPException(status_code=400, detail=f"Failed to fetch article: {exc}") from exc

    quiz_payload = generate_quiz_payload(article)
    quiz = crud.persist_quiz(db, article, quiz_payload)

    return build_quiz_response(quiz)


@app.get("/api/quizzes")
def list_quizzes(db: Session = Depends(get_db)):
    quizzes = crud.list_quizzes(db)
    return [
        {"id": q.id, "url": q.url, "title": q.title, "summary": q.summary or ""}
        for q in quizzes
    ]


@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return build_quiz_response(quiz)


def build_quiz_response(quiz: models.Quiz) -> dict:
    return {
        "id": quiz.id,
        "url": quiz.url,
        "title": quiz.title,
        "summary": quiz.summary,
        "key_entities": json.loads(quiz.key_entities or "{}"),
        "sections": json.loads(quiz.sections or "[]"),
        "quiz": [
            {
                "id": q.id,
                "question": q.question,
                "options": json.loads(q.options or "[]"),
                "answer": q.answer,
                "difficulty": q.difficulty,
                "explanation": q.explanation,
            }
            for q in quiz.questions
        ],
        "related_topics": [t.topic for t in quiz.related_topics],
    }


# Serve frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", response_class=FileResponse)
async def root(request: Request):
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "AI Wiki Quiz Generator API"})
