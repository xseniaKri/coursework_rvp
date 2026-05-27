from fastapi import FastAPI

from src.api.router import api_router
from src.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
