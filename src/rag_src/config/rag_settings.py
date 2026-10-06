from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# C:\Users\hp\PythonProject
BASE_DIR = Path(__file__).resolve().parents[3]


class RAGSettings(BaseSettings):

    GROQ_API_KEY: str

    DOCS_DIR: str = "docs_dir"
    CHROMA_DB_DIR: str = "data/chroma_db"
    CHROMA_COLLECTION: str = "incident_knowledge"

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    SIMILARITY_THRESHOLD: float = 0.50

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


rag_settings = RAGSettings()