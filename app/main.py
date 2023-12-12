from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin_panel.admin import setup_admin
from app.core.config import settings
from app.db.session import engine
from app.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
setup_admin(app, engine)
