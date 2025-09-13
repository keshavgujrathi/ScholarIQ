"""
API v1 Endpoints Package

This package contains all endpoint modules for the v1 API.
"""

from fastapi import APIRouter

router = APIRouter()

# Import all endpoint modules here to register their routes
from . import analyze, demo  # noqa: F401, E402

__all__ = ["router"]
