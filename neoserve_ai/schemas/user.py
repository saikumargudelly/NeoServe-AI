from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

class UserRole(str, Enum):
    """Defines the possible roles for users in the system."""
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"
    SYSTEM = "system"

class UserStatus(str, Enum):
    """Defines the possible statuses for a user account."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class UserBase(BaseModel):
    """Base user model containing common fields."""
    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None and not v.replace('+', '').replace(' ', '').isdigit():
            raise ValueError("Phone number must contain only digits, spaces, and a leading plus")
        return v

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserUpdate(BaseModel):
    """Model for updating an existing user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[UserStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None and not v.replace('+', '').replace(' ', '').isdigit():
            raise ValueError("Phone number must contain only digits, spaces, and a leading plus")
        return v

class UserInDB(UserBase):
    """User model as stored in the database."""
    user_id: str = Field(..., description="Unique identifier for the user")
    hashed_password: str = Field(..., description="Hashed password")
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.CUSTOMER], 
                                description="User's roles and permissions")
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION, 
                             description="Current status of the user account")
    created_at: datetime = Field(default_factory=datetime.utcnow, 
                               description="When the user account was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, 
                               description="When the user account was last updated")
    last_login: Optional[datetime] = Field(None, 
                                         description="When the user last logged in")
    metadata: Dict[str, Any] = Field(default_factory=dict, 
                                   description="Additional user metadata")

class User(UserBase):
    """User model for API responses (excludes sensitive data)."""
    user_id: str = Field(..., description="Unique identifier for the user")
    roles: List[UserRole] = Field(..., description="User's roles and permissions")
    status: UserStatus = Field(..., description="Current status of the user account")
    created_at: datetime = Field(..., description="When the user account was created")
    updated_at: datetime = Field(..., description="When the user account was last updated")
    last_login: Optional[datetime] = Field(None, 
                                         description="When the user last logged in")
    metadata: Dict[str, Any] = Field(default_factory=dict, 
                                   description="Additional user metadata")

class UserInResponse(BaseModel):
    """Wrapper for user data in API responses."""
    user: User

class Token(BaseModel):
    """Authentication token model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of token")
    expires_in: int = Field(..., description="Time in seconds until the token expires")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access tokens")

class TokenData(BaseModel):
    """Data stored in the authentication token."""
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None
    roles: List[UserRole] = []
    exp: Optional[int] = None

class UserSession(BaseModel):
    """Represents a user's active session."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="ID of the user this session belongs to")
    user_agent: Optional[str] = Field(None, description="User agent string from the client")
    ip_address: Optional[str] = Field(None, description="IP address of the client")
    created_at: datetime = Field(default_factory=datetime.utcnow, 
                               description="When the session was created")
    expires_at: datetime = Field(..., description="When the session expires")
    last_activity: datetime = Field(default_factory=datetime.utcnow, 
                                  description="When the session was last active")
    is_active: bool = Field(default=True, description="Whether the session is currently active")
    metadata: Dict[str, Any] = Field(default_factory=dict, 
                                   description="Additional session metadata")
