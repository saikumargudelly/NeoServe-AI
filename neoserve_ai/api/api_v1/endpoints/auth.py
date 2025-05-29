"""
Authentication endpoints for the NeoServe AI API.
"""
from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from neoserve_ai.schemas.user import Token, User, UserCreate, UserInDB
from neoserve_ai.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from neoserve_ai.config.settings import get_config

# Initialize router with prefix and tags
router = APIRouter(prefix="/auth", tags=["authentication"])

# Get configuration
config = get_config()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        form_data: The OAuth2 password request form containing username and password
        
    Returns:
        Token object containing the access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.user_id,
            "roles": user.roles,
        },
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
    }

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate) -> User:
    """
    Register a new user.
    
    Args:
        user_data: The user registration data
        
    Returns:
        The newly created user
        
    Raises:
        HTTPException: If the email is already registered
    """
    from ....utils.auth import get_user, fake_users_db
    
    # Check if user already exists
    if get_user(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user_data.dict()
    hashed_password = get_password_hash(user_dict.pop("password"))
    
    # In a real app, this would be saved to a database
    new_user = UserInDB(
        **user_dict,
        hashed_password=hashed_password,
        user_id=f"user_{len(fake_users_db) + 1}",
        roles=["customer"],  # Default role for new users
        status="active"  # In a real app, you might want to require email verification first
    )
    
    # Add to fake database
    fake_users_db[user_data.email] = new_user.dict()
    
    # Return the user without the hashed password
    return User(
        user_id=new_user.user_id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        phone_number=new_user.phone_number,
        avatar_url=new_user.avatar_url,
        roles=new_user.roles,
        status=new_user.status,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        last_login=new_user.last_login,
        metadata=new_user.metadata
    )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get the current user's profile.
    
    Args:
        current_user: The currently authenticated user
        
    Returns:
        The user's profile information
    """
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Refresh an access token.
    
    Args:
        current_user: The currently authenticated user
        
    Returns:
        A new access token
    """
    # Create a new token with a new expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user.email,
            "user_id": current_user.user_id,
            "roles": current_user.roles,
        },
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
    }
