# AI Wiki Quiz Generator

A minimal FastAPI + vanilla HTML frontend that scrapes a Wikipedia article, generates a quiz using an LLM (Gemini via LangChain when a key is provided, with a deterministic fallback), stores the results in a database, and surfaces a history tab with a details modal.

## Features
- Tab 1: Generate quiz from a Wikipedia URL (scraping via BeautifulSoup, quiz generation via LangChain/Gemini when configured).
- Tab 2: Past quizzes with modal to view full quiz details.
- Stores scraped and generated data in a database (PostgreSQL recommended; SQLite used by default for quick start).
- Sample data and prompt templates included in code.

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL database (or use the default SQLite for local dev)

### Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Environment variables:
- `DATABASE_URL` – SQLAlchemy URL (e.g., `postgresql+psycopg2://user:pass@localhost:5432/quizdb`). Defaults to `sqlite:///./quiz.db`.
- `GOOGLE_API_KEY` – optional; enables Gemini via LangChain for quiz generation.

### Run the app
```bash
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 to use the UI.

## API Endpoints
- `POST /api/quiz` – body: `{ "url": "<wikipedia-url>" }` -> generates, stores, and returns quiz payload.
- `GET /api/quizzes` – list previously generated quizzes.
- `GET /api/quizzes/{id}` – retrieve full quiz payload for a stored quiz.
- `GET /api/health` – health check.

## Sample Data
See `sample_data/alan_turing.json` for example input/output and structure.

## Notes on LLM usage
- Prompt template for quiz generation is defined in `app/llm.py` (`QUIZ_PROMPT`).
- If `GOOGLE_API_KEY` is set, Gemini is called directly via `google-generativeai`. Otherwise, a deterministic fallback generator produces structured quizzes to keep the app functional offline.

## Frontend
- Static HTML/JS in `frontend/index.html` served by FastAPI.
- Two tabs: Generate Quiz and Past Quizzes (with details modal).

## Testing
- No automated tests are included. You can quickly verify by running the app and generating a quiz with a Wikipedia URL.

## Screenshots
- Quiz generation (Tab 1): ![Quiz generation](https://github.com/user-attachments/assets/7ca7b4de-280f-4cca-bb28-aee6dcd709b7)
