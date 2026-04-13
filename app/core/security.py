import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=64,
    )
    return f"{salt.hex()}:{derived_key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, hash_hex = password_hash.split(":", maxsplit=1)
    except ValueError:
        return False

    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=2**14,
        r=8,
        p=1,
        dklen=64,
    )
    return hmac.compare_digest(derived_key.hex(), hash_hex)


def create_access_token(user_id: int) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.auth_access_token_expire_minutes * 60
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": "access",
    }
    token = jwt.encode(
        payload,
        settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
    )
    return token, expires_in


def decode_access_token(token: str) -> dict[str, str]:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    return payload
