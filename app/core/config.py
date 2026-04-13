from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clasificador Inteligente de Documentos con IA"
    app_env: str = Field(default="development")
    app_host: str = "127.0.0.1"
    app_port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/"
        "clasificador_documentos_ia"
    )
    uploads_dir: str = "uploads"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = Field(default=384, gt=0)
    semantic_search_top_k: int = Field(default=5, ge=1, le=20)
    redis_url: str = "redis://127.0.0.1:6379/0"
    celery_broker_url: str = "redis://127.0.0.1:6379/0"
    celery_result_backend: str = "redis://127.0.0.1:6379/1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        allowed = {"development", "test", "production"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            allowed_values = ", ".join(sorted(allowed))
            raise ValueError(f"APP_ENV debe ser uno de: {allowed_values}.")
        return normalized

    @field_validator(
        "database_url",
        "redis_url",
        "celery_broker_url",
        "celery_result_backend",
    )
    @classmethod
    def validate_required_urls(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("La URL no puede estar vacia.")
        if "://" not in normalized:
            raise ValueError("La URL debe incluir un esquema valido, por ejemplo postgresql:// o redis://.")
        return normalized

    @field_validator("uploads_dir", "embedding_model")
    @classmethod
    def validate_non_empty_values(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Este valor no puede estar vacio.")
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
