from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.api_error import ApiErrorResponse, ValidationErrorDetail

DEFAULT_ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "validation_error",
}

ERROR_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ApiErrorResponse,
        "description": "Solicitud invÃ¡lida o regla de negocio no cumplida.",
    },
    status.HTTP_401_UNAUTHORIZED: {
        "model": ApiErrorResponse,
        "description": "Autenticacion requerida o token invalido.",
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ApiErrorResponse,
        "description": "Recurso no encontrado.",
    },
    status.HTTP_409_CONFLICT: {
        "model": ApiErrorResponse,
        "description": "Conflicto con el estado actual del recurso.",
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "model": ApiErrorResponse,
        "description": "Error de validaciÃ³n de entrada.",
    },
}


class ApiError(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message},
            headers=headers,
        )


def bad_request(message: str) -> ApiError:
    return ApiError(status.HTTP_400_BAD_REQUEST, "bad_request", message)


def unauthorized(message: str = "No autenticado.") -> ApiError:
    return ApiError(
        status.HTTP_401_UNAUTHORIZED,
        "unauthorized",
        message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def not_found(message: str) -> ApiError:
    return ApiError(status.HTTP_404_NOT_FOUND, "not_found", message)


def conflict(message: str) -> ApiError:
    return ApiError(status.HTTP_409_CONFLICT, "conflict", message)


def _build_http_error_payload(exc: HTTPException) -> ApiErrorResponse:
    if isinstance(exc.detail, dict):
        code = str(
            exc.detail.get("code", DEFAULT_ERROR_CODES.get(exc.status_code, "http_error"))
        )
        message = str(exc.detail.get("message", "OcurriÃ³ un error en la solicitud."))
        details = exc.detail.get("details")
    else:
        code = DEFAULT_ERROR_CODES.get(exc.status_code, "http_error")
        message = str(exc.detail)
        details = None

    return ApiErrorResponse(code=code, message=message, details=details)


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    payload = _build_http_error_payload(exc)
    response = JSONResponse(status_code=exc.status_code, content=payload.model_dump())
    if exc.headers:
        for header_name, header_value in exc.headers.items():
            response.headers[header_name] = header_value
    return response


async def request_validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = [
        ValidationErrorDetail(
            loc=[str(item) for item in error["loc"]],
            message=error["msg"],
            type=error["type"],
        )
        for error in exc.errors()
    ]
    payload = ApiErrorResponse(
        code="validation_error",
        message="La solicitud no cumple el contrato esperado.",
        details=details,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=payload.model_dump(),
    )
