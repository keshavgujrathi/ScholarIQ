"""
API v1 package

This package contains all API endpoints and routes for version 1 of the ScholarIQ API.
"""

from fastapi import APIRouter

router = APIRouter()

# Import all endpoint modules to register the routes
from . import endpoints  # noqa: F401, E402

__all__ = ["router"]
