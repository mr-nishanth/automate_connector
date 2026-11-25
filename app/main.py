"""Application entry point.

Start the server with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app import __version__
from app.api.items import router as items_router
from app.api.routes import router as root_router


def create_app() -> FastAPI:
    application = FastAPI(title="automate-connector API", version=__version__)
    application.include_router(root_router)
    application.include_router(items_router)
    return application


app = create_app()
