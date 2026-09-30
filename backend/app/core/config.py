from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG Platform"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    PORT: int = 8000
    
    # Database (PostgreSQL/Neon)
    DATABASE_URL: str
    
    # AI & Vector Store (Opsional/Sesuai Kebutuhan PRD)
    OPENAI_API_KEY: Optional[str] = None
    CHROMA_DB_DIR: str = "./chroma_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()