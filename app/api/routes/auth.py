from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import ERROR_RESPONSES, conflict, unauthorized
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Crea un usuario local con contraseña hasheada para autenticación JWT.",
    responses={
        status.HTTP_409_CONFLICT: ERROR_RESPONSES[status.HTTP_409_CONFLICT],
        status.HTTP_422_UNPROCESSABLE_CONTENT: ERROR_RESPONSES[status.HTTP_422_UNPROCESSABLE_CONTENT],
    },
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise conflict("Ya existe un usuario registrado con ese correo.")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesion",
    description="Valida credenciales y devuelve un access token JWT.",
    responses={
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSES[status.HTTP_401_UNAUTHORIZED],
        status.HTTP_422_UNPROCESSABLE_CONTENT: ERROR_RESPONSES[status.HTTP_422_UNPROCESSABLE_CONTENT],
    },
)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise unauthorized("Credenciales invalidas.")

    token, expires_in = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer", expires_in=expires_in)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario autenticado",
    description="Devuelve el usuario asociado al token Bearer actual.",
    responses={
        status.HTTP_401_UNAUTHORIZED: ERROR_RESPONSES[status.HTTP_401_UNAUTHORIZED],
    },
)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
