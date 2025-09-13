from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
from pydantic import ConfigDict

from app.models.user import UserRole

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.STUDENT
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user data."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    """Base schema for user data in the database."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    """Schema for user data returned by the API."""
    pass

class UserInDB(UserInDBBase):
    """Schema for user data in the database (includes hashed password)."""
    hashed_password: str

class Token(BaseModel):
    """Schema for JWT token."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data."""
    email: Optional[str] = None
    scopes: List[str] = []
