from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG Platform"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    OPENAI_API_KEY: Optional[str] = None
    CHROMA_DB_DIR: str = "./chroma_db"
    MAX_UPLOAD_BYTES: int = 5_000_000
    MAX_CHAT_MESSAGE_LENGTH: int = 4_000
    CONVERSATION_RETENTION_DAYS: int = 365
    CORS_ORIGINS: str = "http://localhost:3000"
    MOCK_AUTH_ENABLED: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def default_to_local_database(cls, value: str | None) -> str:
        return value.strip() if value and value.strip() else "sqlite+aiosqlite:///./sql_app.db"

settings = Settings()