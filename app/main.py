from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

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
)

app.include_router(api_router)
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")


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


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "API funcionando"}


@app.get("/health/live", tags=["health"])
def health_live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", response_model=HealthReadyResponse, tags=["health"])
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