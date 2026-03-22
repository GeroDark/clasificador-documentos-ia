from redis import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import SessionLocal


def check_database() -> tuple[bool, str]:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as exc:
        return False, str(exc)
    finally:
        db.close()


def check_redis() -> tuple[bool, str]:
    settings = get_settings()
    client = Redis.from_url(settings.redis_url, decode_responses=True)

    try:
        client.ping()
        return True, "connected"
    except Exception as exc:
        return False, str(exc)
    finally:
        client.close()