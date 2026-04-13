from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clasificador Inteligente de Documentos con IA"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/clasificador_documentos_ia"
    uploads_dir: str = "uploads"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384
    semantic_search_top_k: int = 5
    redis_url: str = "redis://127.0.0.1:6379/0"
    celery_broker_url: str = "redis://127.0.0.1:6379/0"
    celery_result_backend: str = "redis://127.0.0.1:6379/1"
    auth_secret_key: str = "change-me-in-development-32-bytes"
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = Field(default=60, ge=1, le=1440)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    @field_validator("auth_secret_key")
    @classmethod
    def validate_auth_secret_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Este valor no puede estar vacio.")
        if len(normalized) < 32:
            raise ValueError("AUTH_SECRET_KEY debe tener al menos 32 caracteres.")
        return normalized

    @field_validator("auth_algorithm")
    @classmethod
    def validate_auth_algorithm(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Este valor no puede estar vacio.")
        return normalized

@lru_cache
def get_settings() -> Settings:
    return Settings()
