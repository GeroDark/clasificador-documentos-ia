from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="API para clasificación, extracción, resumen y búsqueda semántica de documentos.",
)

app.include_router(api_router)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "API funcionando"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
    }