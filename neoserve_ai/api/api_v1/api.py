"""
Main API router that includes all versioned API endpoints.
"""
from fastapi import APIRouter

from .endpoints import routers as endpoint_routers

# Create API router
api_router = APIRouter()

# Include all endpoint routers
for router in endpoint_routers:
    api_router.include_router(router)

# You can also include additional routers here if needed
# api_router.include_router(some_other_router, prefix="/some-prefix", tags=["some-tag"])
