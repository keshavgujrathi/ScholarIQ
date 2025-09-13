from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.logging import logger

# Import all endpoint routers
from .endpoints import auth

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=False,
)

# Create API router
api_router = APIRouter()

# Include API routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
    dependencies=[Depends(oauth2_scheme)],
)

# Health check endpoint
@api_router.get(
    "/health",
    status_code=200,
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="API status information",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "version": "1.0.0",
                        "environment": "development",
                    }
                }
            },
        },
    },
)
async def health_check() -> dict:
    """
    Health check endpoint that returns the API status and version information.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "service": settings.APP_NAME,
    }
