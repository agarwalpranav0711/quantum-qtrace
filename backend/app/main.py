"""Main FastAPI application entry point for Q-TRACE Core API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging, get_logger
from backend.app.core.exceptions import (
    QTraceException,
    qtrace_exception_handler,
    unhandled_exception_handler,
)
from backend.app.database.session import init_db
from backend.app.storage.service import get_storage_service
from backend.app.api.health import get_health
from backend.app.schemas.health import HealthResponse
from backend.app.api.router import api_v1_router

settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    setup_logging(settings.LOG_LEVEL)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    init_db()
    storage = get_storage_service()
    storage.ensure_storage_dirs()
    logger.info(f"Storage subsystem ready at {storage.root}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title="Q-TRACE Core API",
    description=(
        "Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform API. "
        "Provides cryptographic evidence preservation (WORM), classical and quantum image analysis, "
        "and investigative case management."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handlers
app.add_exception_handler(QTraceException, qtrace_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router)


@app.get("/health", response_model=HealthResponse, tags=["Root"])
def root_health():
    """Root health check redirecting to standard health schema."""
    return get_health(settings)


@app.get("/", tags=["Root"])
def root_info():
    """Root metadata endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "description": "Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": "/health",
    }
