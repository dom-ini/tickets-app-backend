from fastapi import APIRouter

from app.auth.api.v1.router import api_router as auth_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)
api_router.include_router(auth_router)
