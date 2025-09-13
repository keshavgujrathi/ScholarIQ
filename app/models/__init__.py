# Import all models here so they are registered with SQLAlchemy
from .base import BaseModel
from .user import User, UserRole
from .student import Student
from .assessment import Assessment

# This will be used by SQLAlchemy to discover all models
__all__ = ["BaseModel", "User", "UserRole", "Student", "Assessment"]
