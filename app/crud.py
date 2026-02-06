from __future__ import annotations

import json
from typing import List

from sqlalchemy.orm import Session

from . import models
from .scraper import ScrapeResult


def persist_quiz(db: Session, article: ScrapeResult, quiz_payload: dict) -> models.Quiz:
    existing = db.query(models.Quiz).filter(models.Quiz.url == article.url).first()
    if existing:
        return existing

    quiz = models.Quiz(
        url=article.url,
        title=article.title,
        summary=article.summary,
        key_entities=json.dumps(article.key_entities),
        sections=json.dumps(article.sections),
    )
    db.add(quiz)
    db.flush()

    for q in quiz_payload.get("quiz", []):
        question = models.Question(
            quiz_id=quiz.id,
            question=q.get("question", ""),
            options=json.dumps(q.get("options", [])),
            answer=q.get("answer", ""),
            difficulty=q.get("difficulty") or "",
            explanation=q.get("explanation") or "",
        )
        db.add(question)

    for topic in quiz_payload.get("related_topics", []):
        db.add(models.RelatedTopic(quiz_id=quiz.id, topic=topic))

    db.commit()
    db.refresh(quiz)
    return quiz


def list_quizzes(db: Session) -> List[models.Quiz]:
    return db.query(models.Quiz).order_by(models.Quiz.id.desc()).all()


def get_quiz(db: Session, quiz_id: int) -> models.Quiz | None:
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
