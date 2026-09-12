"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.errors import DomainException
from app.core.logging import setup_logging
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager: initial setup and teardown."""
    setup_logging()
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        import logging

        logging.getLogger("app").warning(
            "Database auto-provisioning skipped or unavailable on boot: %s", exc
        )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API for Coffee Shop Online Ordering System (Sprint 1 MVP)",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers enforcing standardized error formats
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle domain business rule exceptions with consistent JSON shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle payload validation failures with standardized 422 format."""
    # Simplify error details
    formatted_errors = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        formatted_errors.append({"field": field_path, "issue": err.get("msg")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "validation_failed",
            "message": "Field constraints violated",
            "details": formatted_errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Normalize HTTPException responses into standard shape."""
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        content = exc.detail
    else:
        content = {
            "code": "http_error",
            "message": str(exc.detail),
            "details": None,
        }
    headers = getattr(exc, "headers", None)
    return JSONResponse(status_code=exc.status_code, content=content, headers=headers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unexpected server errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "internal_error",
            "message": "An unexpected internal error occurred",
            "details": None,
        },
    )


# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"], summary="Health check endpoint")
def health_check() -> dict:
    """Liveness probe returning application operational status."""
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": "1.0.0"}
