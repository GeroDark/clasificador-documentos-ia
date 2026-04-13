from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.errors import http_exception_handler, request_validation_exception_handler
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import log_event, setup_logging
from app.schemas.health import HealthComponentResponse, HealthReadyResponse
from app.services.health import check_database, check_redis

settings = get_settings()
setup_logging()

Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version="0.9.0",
    description="API para clasificación, extracción, resumen, búsqueda semántica y consulta inteligente de documentos.",
    openapi_tags=[
        {
            "name": "documents",
            "description": "Carga, consulta y enriquecimiento de documentos.",
        },
        {
            "name": "jobs",
            "description": "Seguimiento de jobs de procesamiento asíncrono.",
        },
        {
            "name": "search",
            "description": "Consulta semántica sobre chunks indexados.",
        },
        {
            "name": "ask",
            "description": "Preguntas y respuestas sobre contenido documental.",
        },
        {
            "name": "health",
            "description": "Estado operativo de dependencias del backend.",
        },
        {"name": "root", "description": "Información básica del servicio."},
    ],
)

app.include_router(api_router)
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = uuid4().hex[:12]
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        log_event(
            "http",
            event="request_error",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
            error=str(exc),
        )
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    log_event(
        "http",
        event="request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    return response


@app.get(
    "/",
    tags=["root"],
    summary="Verificar disponibilidad base del servicio",
    description="Retorna una respuesta simple para confirmar que la API está accesible.",
)
def read_root() -> dict[str, str]:
    return {"message": "API funcionando"}


@app.get(
    "/health/live",
    tags=["health"],
    summary="Validar liveness de la API",
    description="Confirma que el proceso HTTP está levantado y respondiendo.",
)
def health_live() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/health/ready",
    response_model=HealthReadyResponse,
    tags=["health"],
    summary="Validar readiness del backend",
    description="Comprueba conectividad con base de datos y Redis antes de operar.",
)
def health_ready():
    db_ok, db_detail = check_database()
    redis_ok, redis_detail = check_redis()

    payload = HealthReadyResponse(
        status="ok" if db_ok and redis_ok else "degraded",
        database=HealthComponentResponse(ok=db_ok, detail=db_detail),
        redis=HealthComponentResponse(ok=redis_ok, detail=redis_detail),
    )

    status_code = 200 if payload.status == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload.model_dump())
