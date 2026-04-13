import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accept_valid_test_environment() -> None:
    settings = Settings(
        app_env="test",
        database_url="postgresql+psycopg://postgres:postgres@127.0.0.1:5432/test_db",
        redis_url="redis://127.0.0.1:6379/0",
        celery_broker_url="redis://127.0.0.1:6379/0",
        celery_result_backend="redis://127.0.0.1:6379/1",
    )

    assert settings.app_env == "test"
    assert settings.semantic_search_top_k == 5


def test_settings_reject_invalid_app_env() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(app_env="staging")

    assert "APP_ENV debe ser uno de" in str(exc_info.value)


def test_settings_reject_empty_uploads_dir() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(uploads_dir="   ")

    assert "Este valor no puede estar vacio." in str(exc_info.value)


def test_settings_reject_url_without_scheme() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(database_url="127.0.0.1:5432/sin-esquema")

    assert "La URL debe incluir un esquema valido" in str(exc_info.value)
