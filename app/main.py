from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.web.router import web_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(web_router)

    @app.get("/")
    async def root():
        return RedirectResponse(url="/events")

    return app


app = create_app()
