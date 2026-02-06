from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .config import get_settings
from .scraper import ScrapeResult

settings = get_settings()

QUIZ_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that creates factual quizzes from Wikipedia articles. "
            "Generate 5-10 multiple-choice questions with four options (A-D), the correct answer, "
            "a short explanation, and difficulty (easy, medium, hard). Also suggest 5 related Wikipedia topics. "
            "Return ONLY valid JSON with keys: quiz (list of questions), related_topics (list of strings).",
        ),
        (
            "human",
            "Article content:\n{article_text}\n\nRespond in JSON.",
        ),
    ]
)


def _try_llm(article_text: str) -> Optional[Dict[str, Any]]:
    llm = None
    if settings.google_api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2, max_output_tokens=1024)
        except Exception:
            llm = None

    if llm is None:
        return None

    chain = QUIZ_PROMPT | llm | StrOutputParser()
    output = chain.invoke({"article_text": article_text})
    try:
        return json.loads(output)
    except Exception:
        return None


def _fallback_quiz(article: ScrapeResult) -> Dict[str, Any]:
    questions: List[Dict[str, Any]] = []
    for idx, section in enumerate(article.sections[:10] or ["Overview"]):
        question = f"What is highlighted in the '{section}' section of the article?"
        options = [
            f"Details about {section}",
            "Irrelevant background",
            "Unrelated biography",
            "Completely different topic",
        ]
        questions.append(
            {
                "question": question,
                "options": options,
                "answer": options[0],
                "difficulty": "easy" if idx < 3 else "medium",
                "explanation": f"The section titled '{section}' focuses on this topic.",
            }
        )
    related_topics = article.key_entities.get("people", [])[:3] + article.sections[:2]
    if not related_topics:
        related_topics = ["Wikipedia", "History", "Science"]
    return {"quiz": questions[:10], "related_topics": related_topics[:10]}


def generate_quiz_payload(article: ScrapeResult) -> Dict[str, Any]:
    # Try LLM first; otherwise deterministic fallback
    llm_response = _try_llm(article.raw_text)
    if llm_response and "quiz" in llm_response:
        return llm_response
    return _fallback_quiz(article)
