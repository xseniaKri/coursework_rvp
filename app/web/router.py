from fastapi import APIRouter

from app.web import admin, auth, events, reports

web_router = APIRouter()
web_router.include_router(auth.router)
web_router.include_router(events.router)
web_router.include_router(admin.router)
web_router.include_router(reports.router)
