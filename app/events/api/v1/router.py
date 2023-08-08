from fastapi import APIRouter

from app.events.api.v1.endpoints import artists, events

api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(artists.router, prefix="/artists", tags=["artists"])
