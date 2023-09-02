from fastapi import APIRouter

from app.events.api.v1.endpoints import event_types, events, speakers

api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(speakers.router, prefix="/speakers", tags=["speakers"])
api_router.include_router(event_types.router, prefix="/event-types", tags=["event types"])
