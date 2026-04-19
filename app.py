"""FastAPI application entry point.

Creates the app, configures CORS, and includes API routers.
"""
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Environment variables with defaults
_api_title = os.getenv("API_TITLE", "IA Dashboard desde Excel")
_api_version = os.getenv("API_VERSION", "0.1.0")
_cors_raw = os.getenv("CORS_ORIGINS", "")
allow_origins = _cors_raw.split(",") if _cors_raw else ["*"]


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup: create tables if they don't exist."""
    from database import engine, Base
    import models  # noqa: F401 — ensure models are registered on Base

    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=_api_title, version=_api_version, lifespan=lifespan)

# CORS — configurable via CORS_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from routes.users import router as users_router
from routes.projects import router as projects_router
from routes.tables import router as tables_router
from routes.generate import router as generate_router

app.include_router(users_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(tables_router, prefix="/api")
app.include_router(generate_router, prefix="/api")