"""
API Router for v1 API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, waste, biochar, carbon_credit, organization

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(waste.router)
api_router.include_router(biochar.router)
api_router.include_router(carbon_credit.router)
api_router.include_router(organization.router)