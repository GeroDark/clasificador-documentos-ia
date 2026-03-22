from fastapi import APIRouter

from app.api.routes.ask import router as ask_router
from app.api.routes.documents import router as documents_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(documents_router)
api_router.include_router(search_router)
api_router.include_router(ask_router)
api_router.include_router(jobs_router)