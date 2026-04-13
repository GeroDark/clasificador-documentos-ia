from app.core.security import decode_access_token
from app.models.user import User


def test_register_creates_user_with_hashed_password(client, db_session) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": "nuevo@example.com",
            "password": "Password123",
            "full_name": "Nuevo Usuario",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "nuevo@example.com"
    assert payload["full_name"] == "Nuevo Usuario"

    stored_user = db_session.query(User).filter(User.email == "nuevo@example.com").one()
    assert stored_user.password_hash != "Password123"
    assert ":" in stored_user.password_hash


def test_register_rejects_duplicate_email(client, user_factory) -> None:
    user_factory(email="duplicado@example.com")

    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicado@example.com",
            "password": "Password123",
            "full_name": "Duplicado",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Ya existe un usuario registrado con ese correo.",
        "details": None,
    }


def test_login_returns_valid_bearer_token(client, user_factory) -> None:
    user = user_factory(email="login@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "Password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] > 0

    token_payload = decode_access_token(payload["access_token"])
    assert token_payload["sub"] == str(user.id)
    assert token_payload["type"] == "access"


def test_login_rejects_invalid_credentials(client, user_factory) -> None:
    user_factory(email="login@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "Password999"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Credenciales invalidas.",
        "details": None,
    }


def test_me_returns_authenticated_user(client, auth_headers) -> None:
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "usuario@example.com"
    assert payload["is_active"] is True


def test_protected_documents_endpoint_returns_401_without_token(client) -> None:
    response = client.get("/api/documents/")

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Token de acceso requerido.",
        "details": None,
    }


def test_protected_search_endpoint_returns_401_without_token(client) -> None:
    response = client.get("/api/search/semantic/", params={"q": "contrato"})

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Token de acceso requerido.",
        "details": None,
    }


def test_protected_ask_endpoint_returns_401_without_token(client) -> None:
    response = client.post("/api/ask/", json={"question": "¿Cuál es el monto?"})

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Token de acceso requerido.",
        "details": None,
    }
