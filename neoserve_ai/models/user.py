"""
User model for the application.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Model for creating a new user (includes password)."""
    password: str

class UserInDB(UserBase):
    """User model for storing in the database."""
    id: int
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class User(UserBase):
    """User model for API responses (excludes sensitive data)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
