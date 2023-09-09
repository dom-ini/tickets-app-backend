from fastapi import APIRouter

from app.tickets.api.v1.endpoints import ticket_categories, tickets

api_router = APIRouter()
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(ticket_categories.router, prefix="/ticket-categories", tags=["ticket categories"])
