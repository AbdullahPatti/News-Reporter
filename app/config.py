from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Application
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # AI
    GEMINI_API_KEY: Optional[str] = None

    # Email
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "News Reporter <onboarding@resend.dev>"

    # Optional / Future
    YOUTUBE_API_KEY: Optional[str] = None
    INTERNAL_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()