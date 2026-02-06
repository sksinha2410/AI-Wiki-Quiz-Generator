import os
from functools import lru_cache


class Settings:
    app_name: str = "AI Wiki Quiz Generator"
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./quiz.db"
    )  # default for local dev; recommend Postgres in production
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    allow_origins: list[str] = ["*"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
