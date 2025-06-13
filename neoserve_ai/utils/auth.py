"""
Authentication and authorization utilities for the NeoServe AI API.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Set up logging
logger = logging.getLogger(__name__)
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext

from ..schemas.user import User, UserInDB, TokenData, UserRole
from ..config.settings import get_config

# Get configuration
settings = get_config()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=False
)

# JWT configuration
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Mock user database (in a real app, this would be a database)
# This is just for demonstration purposes
fake_users_db = {
    "customer1@example.com": {
        "user_id": "user_123",
        "email": "customer1@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "hashed_password": pwd_context.hash("password123"),
        "roles": ["customer"],
        "status": "active",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "metadata": {}
    },
    "agent1@example.com": {
        "user_id": "user_456",
        "email": "agent1@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "hashed_password": pwd_context.hash("password123"),
        "roles": ["agent"],
        "status": "active",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "metadata": {}
    },
    "admin@example.com": {
        "user_id": "user_789",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "hashed_password": pwd_context.hash("admin123"),
        "roles": ["admin"],
        "status": "active",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "metadata": {}
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to compare against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def get_user(email: str) -> Optional[UserInDB]:
    """
    Get a user by email.
    
    Args:
        email: The user's email address
        
    Returns:
        Optional[UserInDB]: The user if found, None otherwise
    """
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)
    return None

def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user.
    
    Args:
        email: The user's email address
        password: The plain text password
        
    Returns:
        Optional[UserInDB]: The authenticated user if successful, None otherwise
    """
    user = get_user(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: The JWT token
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        logger.error("No token provided")
        raise credentials_exception
    
    # Log token prefix for debugging (don't log full token for security)
    token_prefix = token[:10] if len(token) > 10 else token
    logger.debug(f"Attempting to verify token: {token_prefix}...")
    logger.debug(f"Using JWT secret key: {JWT_SECRET_KEY[:5]}...")
    logger.debug(f"Using algorithm: {JWT_ALGORITHM}")
    
    try:
        # Decode the token with verification
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True}
        )
        
        logger.debug(f"Successfully decoded token payload: {payload}")
        
        email: str = payload.get("sub")
        if not email:
            logger.error("No 'sub' claim found in token")
            raise credentials_exception
            
        token_data = TokenData(
            email=email,
            user_id=payload.get("user_id"),
            roles=payload.get("roles", [])
        )
        
        logger.debug(f"Extracted token data: {token_data}")
        
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}", exc_info=True)
        raise credentials_exception
    
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return User(
        user_id=user.user_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        avatar_url=user.avatar_url,
        roles=user.roles,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        metadata=user.metadata
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def has_role(required_roles: List[str]):
    """
    Dependency to check if the current user has any of the required roles.
    
    Args:
        required_roles: List of role names that are allowed
        
    Returns:
        Callable: The dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        """Check if the current user has any of the required roles."""
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Common role dependencies
admin_required = has_role(["admin"])
agent_required = has_role(["agent", "admin"])
any_authenticated = has_role(["customer", "agent", "admin"])
