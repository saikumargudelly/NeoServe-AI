"""
API v1 endpoints package.

This package contains all the API endpoints for version 1 of the NeoServe AI API.
"""

from .auth import router as auth_router
from .chat import router as chat_router

# List of all endpoint routers
routers = [
    auth_router,
    chat_router,
]

__all__ = ["routers"]
