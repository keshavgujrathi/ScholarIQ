from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import uuid
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api_v1.api import api_router
from app.core.database import init_db, get_db, SessionLocal

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    logger.info("Starting ScholarIQ application...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    
    logger.info("ScholarIQ application started successfully")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down ScholarIQ application...")
    # Close database connections
    db = SessionLocal()
    db.close()
    logger.info("ScholarIQ application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="ScholarIQ API",
    description="AI-Powered Student Analytics Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None,
        },
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
            },
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise

# Mount static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with detailed error messages."""
    errors: Dict[str, Any] = {"detail": []}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body' in loc
        errors["detail"].append(
            {
                "loc": [field],
                "msg": error["msg"],
                "type": error["type"],
            }
        )
    
    logger.warning(
        "Request validation failed",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "errors": errors,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=errors,
    )

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle all unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled exception occurred",
        exc_info=True,
        extra={
            "request_id": request_id,
            "error": str(exc),
            "type": type(exc).__name__,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )

# Health check endpoint
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Service is healthy"},
        500: {"description": "Service is unhealthy"},
    },
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint that verifies the service is running correctly.
    
    Returns:
        Dict with service status information
    """
    # Check database connection
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    finally:
        db.close()
    
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "database": db_status,
    }

# Root endpoint
@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Welcome message and API information"},
    },
)
async def root() -> Dict[str, Any]:
    """
    Root endpoint that provides basic API information.
    
    Returns:
        Dict with welcome message and API information
    """
    return {
        "message": "Welcome to ScholarIQ API - AI-Powered Student Analytics Platform",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "documentation": "/docs",
        "status": "operational",
    }
