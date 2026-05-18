"""
Organization management API endpoints.
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
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationStats
)
from app.models.organization import Organization
from sqlalchemy import select, func

router = APIRouter(prefix="/organizations", tags=["Organizations"])
logger = get_logger(__name__)


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new organization."""
    if not has_permission(current_user.role, "organization:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    existing = await db.execute(
        select(Organization).where(Organization.slug == org_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )

    org = Organization(
        name=org_data.name,
        slug=org_data.slug,
        description=org_data.description,
        organization_type=org_data.organization_type,
        registration_number=org_data.registration_number,
        tax_id=org_data.tax_id,
        address=org_data.address,
        city=org_data.city,
        state=org_data.state,
        country=org_data.country,
        postal_code=org_data.postal_code,
        phone=org_data.phone,
        email=org_data.email,
        website=org_data.website,
        industry=org_data.industry,
    )

    db.add(org)
    await db.flush()
    await db.refresh(org)

    await db.commit()
    logger.info(f"Organization created: {org.name}")
    return OrganizationResponse.model_validate(org)


@router.get("/", response_model=list[OrganizationResponse])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all organizations."""
    result = await db.execute(
        select(Organization)
        .where(Organization.deleted_at.is_(None))
        .order_by(Organization.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    orgs = result.scalars().all()
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization by ID."""
    result = await db.execute(
        select(Organization).where(
            Organization.id == org_id,
            Organization.deleted_at.is_(None)
        )
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return OrganizationResponse.model_validate(org)


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_data: OrganizationUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update organization."""
    if not has_permission(current_user.role, "organization:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    result = await db.execute(
        select(Organization).where(
            Organization.id == org_id,
            Organization.deleted_at.is_(None)
        )
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    update_dict = org_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(org, key, value)

    await db.flush()
    await db.refresh(org)
    await db.commit()

    return OrganizationResponse.model_validate(org)


@router.get("/{org_id}/stats", response_model=OrganizationStats)
async def get_organization_stats(
    org_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization statistics."""
    result = await db.execute(
        select(Organization).where(
            Organization.id == org_id,
            Organization.deleted_at.is_(None)
        )
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    from app.models.waste import WasteRecord
    from app.models.biochar import BiocharRecord
    from app.models.carbon_credit import CarbonCredit
    from app.models.verification import VerificationRequest

    waste_count = await db.scalar(
        select(func.count(WasteRecord.id)).where(
            WasteRecord.organization_id == org_id,
            WasteRecord.deleted_at.is_(None)
        )
    )

    biochar_count = await db.scalar(
        select(func.count(BiocharRecord.id)).where(
            BiocharRecord.organization_id == org_id,
            BiocharRecord.deleted_at.is_(None)
        )
    )

    credit_count = await db.scalar(
        select(func.count(CarbonCredit.id)).where(
            CarbonCredit.organization_id == org_id,
            CarbonCredit.deleted_at.is_(None)
        )
    )

    pending_verifications = await db.scalar(
        select(func.count(VerificationRequest.id)).where(
            VerificationRequest.organization_id == org_id,
            VerificationRequest.status == "pending"
        )
    )

    return OrganizationStats(
        total_carbon_credits=org.total_carbon_credits or 0,
        total_waste_processed=org.total_waste_processed or 0,
        total_emissions_reduced=org.total_emissions_reduced or 0,
        waste_records_count=waste_count or 0,
        biochar_records_count=biochar_count or 0,
        carbon_credits_count=credit_count or 0,
        pending_verifications=pending_verifications or 0
    )