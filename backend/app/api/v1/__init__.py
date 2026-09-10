from fastapi import APIRouter
from .ask import router as ask_router
from .health import router as health_router

api_router = APIRouter()
api_router.include_router(ask_router)
api_router.include_router(health_router)
