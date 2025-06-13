"""
Token schemas for authentication.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: Optional[str] = None  # Changed from int to str to handle email/username
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
