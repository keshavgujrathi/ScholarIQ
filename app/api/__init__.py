from fastapi import APIRouter

from app.api.api_v1.api import api_router as api_v1_router

# Create main API router
api_router = APIRouter()

# Include API versioned routers
api_router.include_router(api_v1_router, prefix="/v1")
