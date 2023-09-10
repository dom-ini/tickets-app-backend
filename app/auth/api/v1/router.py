from fastapi import APIRouter

from app.auth.api.v1.endpoints import login, password_reset, users, verify_account

api_router = APIRouter()
api_router.include_router(login.router, prefix="/auth", tags=["authentication"])
api_router.include_router(password_reset.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(verify_account.router, prefix="/auth", tags=["authentication"])
