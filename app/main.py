from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="API para clasificación, extracción, resumen y búsqueda semántica de documentos.",
)

app.include_router(api_router)
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "API funcionando"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
    }