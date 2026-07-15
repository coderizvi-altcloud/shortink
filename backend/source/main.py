"""FastAPI application bootstrap."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.source.api.routes import redirect_router, shortlink_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def initialize_backend_application() -> FastAPI:
    app = FastAPI(
        title="Shortink",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    # Allow local Vite UI and other frontends to call the hosted API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(shortlink_router)
    app.include_router(redirect_router)
    return app


backend_app = initialize_backend_application()


def create_database_tables() -> None:
    return None
