"""
Dependencies for FastAPI endpoints.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from neoserve_ai.models.user import UserInDB
from neoserve_ai.schemas.token import TokenPayload
from neoserve_ai.config.settings import get_config

# Get configuration
settings = get_config()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

# Mock user data for development
MOCK_USER = UserInDB(
    id=1,
    username="dev_user",
    email="dev@example.com",
    hashed_password="",
    full_name="Development User",
    is_active=True,
    is_superuser=False
)

async def get_current_user_or_none(token: str = Depends(oauth2_scheme)) -> Optional[UserInDB]:
    """
    Get the current user from the token, or return None if no token is provided.
    In development, returns a mock user if no token is provided.
    """
    # In development, return a mock user if no token is provided
    if settings.ENVIRONMENT == "development" and not token:
        return MOCK_USER
    
    # If no token and not in development, return None
    if not token:
        return None
    
    try:
        # Try to decode the token
        if not token or token == 'null' or token == 'undefined':
            if settings.ENVIRONMENT == "development":
                return MOCK_USER
            return None
            
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception) as e:
        # In development, return a mock user if token is invalid
        if settings.ENVIRONMENT == "development":
            print(f"JWT Error: {str(e)}")
            return MOCK_USER
        return None
    
    # In a real app, you would fetch the user from the database here
    # For now, we'll return the mock user with the token's user ID
    mock_user = MOCK_USER.model_copy(update={"id": token_data.sub, "username": f"user_{token_data.sub}"})
    return mock_user

async def get_optional_user(
    current_user: Optional[UserInDB] = Depends(get_current_user_or_none)
) -> Optional[UserInDB]:
    """
    Dependency that allows unauthenticated access but provides the user if available.
    In development, returns a mock user if no user is authenticated.
    """
    if settings.ENVIRONMENT == "development" and not current_user:
        return MOCK_USER
    return current_user
