"""
Carbon credit API endpoints for managing carbon credits.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import has_permission
from app.schemas.user import UserResponse
from app.schemas.carbon_credit import (
    CarbonCreditResponse,
    CarbonCreditStats,
    CarbonCreditRetire
)
from app.services.carbon_credit import CarbonCreditService

router = APIRouter(prefix="/carbon-credits", tags=["Carbon Credits"])
logger = get_logger(__name__)


@router.get("/", response_model=list[CarbonCreditResponse])
async def get_carbon_credits(
    organization_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get carbon credits with pagination and filters."""
    org_id = UUID(organization_id) if organization_id else None

    if not has_permission(current_user.role, "admin:all"):
        org_id = UUID(current_user.organization_id) if current_user.organization_id else None

    credits = await CarbonCreditService.get_credits_by_organization(
        db,
        organization_id=org_id,
        skip=skip,
        limit=limit
    )

    return [CarbonCreditResponse.model_validate(c) for c in credits]


@router.get("/{credit_id}", response_model=CarbonCreditResponse)
async def get_carbon_credit(
    credit_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get carbon credit by ID."""
    credit = await CarbonCreditService.get_credit_by_id(db, credit_id)

    if not credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carbon credit not found"
        )

    return CarbonCreditResponse.model_validate(credit)


@router.get("/serial/{serial_number}", response_model=CarbonCreditResponse)
async def get_carbon_credit_by_serial(
    serial_number: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get carbon credit by serial number."""
    credit = await CarbonCreditService.get_credit_by_serial(db, serial_number)

    if not credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carbon credit not found"
        )

    return CarbonCreditResponse.model_validate(credit)


@router.post("/{credit_id}/retire", response_model=CarbonCreditResponse)
async def retire_carbon_credit(
    credit_id: UUID,
    retire_data: CarbonCreditRetire,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retire carbon credit."""
    if not has_permission(current_user.role, "carbon_credit:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    credit = await CarbonCreditService.retire_credit(
        db,
        credit_id,
        retire_data.reason
    )

    if not credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carbon credit not found"
        )

    await db.commit()
    return CarbonCreditResponse.model_validate(credit)


@router.get("/stats/summary", response_model=CarbonCreditStats)
async def get_carbon_credit_stats(
    organization_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get carbon credit statistics."""
    org_id = UUID(organization_id) if organization_id else None

    if not has_permission(current_user.role, "admin:all"):
        org_id = UUID(current_user.organization_id) if current_user.organization_id else None

    credits = await CarbonCreditService.get_credits_by_organization(
        db,
        organization_id=org_id,
        skip=0,
        limit=10000
    )

    total_credits = sum(c.quantity for c in credits)
    pending_credits = sum(c.quantity for c in credits if c.status == "pending")
    issued_credits = sum(c.quantity for c in credits if c.status == "issued")
    retired_credits = sum(c.quantity for c in credits if c.is_retired)
    verified_credits = sum(c.quantity for c in credits if c.verification_level in ["verified", "gold"])

    credits_by_category: dict[str, float] = {}
    credits_by_status: dict[str, float] = {}

    for credit in credits:
        credits_by_category[credit.category] = credits_by_category.get(credit.category, 0) + credit.quantity
        credits_by_status[credit.status] = credits_by_status.get(credit.status, 0) + credit.quantity

    return CarbonCreditStats(
        total_credits=total_credits,
        pending_credits=pending_credits,
        issued_credits=issued_credits,
        retired_credits=retired_credits,
        verified_credits=verified_credits,
        credits_by_category=credits_by_category,
        credits_by_status=credits_by_status
    )