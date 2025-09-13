from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel

class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"

class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean(), default=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    # students = relationship("Student", back_populates="user")
    
    def __init__(self, email: str, hashed_password: str, full_name: str = None, role: UserRole = UserRole.STUDENT):
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_teacher(self) -> bool:
        """Check if user has teacher role."""
        return self.role == UserRole.TEACHER
    
    @property
    def is_student(self) -> bool:
        """Check if user has student role."""
        return self.role == UserRole.STUDENT
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
