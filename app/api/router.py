from fastapi import APIRouter

from app.api import auth, categories, events, structure_units, users_admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(structure_units.router, prefix="/structure-units", tags=["structure-units"])
api_router.include_router(users_admin.router, prefix="/users", tags=["users"])
