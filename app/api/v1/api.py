from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, shipments, feedback, support_tickets

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(support_tickets.router, prefix="/support-tickets", tags=["support-tickets"])
