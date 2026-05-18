"""
Biochar management API endpoints for tracking biochar production and application.
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
from app.schemas.biochar import (
    BiocharRecordCreate,
    BiocharRecordUpdate,
    BiocharRecordResponse,
    BiocharCalculationRequest,
    BiocharCalculationResponse
)
from app.services.biochar import BiocharService
from app.services.carbon_credit import CarbonCreditService
from app.formula_engine.base import formula_engine

router = APIRouter(prefix="/biochar", tags=["Biochar"])
logger = get_logger(__name__)


@router.post("/", response_model=BiocharRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_biochar_record(
    biochar_data: BiocharRecordCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new biochar record with carbon credit calculation."""
    try:
        biochar_record = await BiocharService.create_biochar_record(
            db,
            biochar_data,
            created_by_id=UUID(current_user.id)
        )

        carbon_credit = await CarbonCreditService.generate_credit_from_biochar(
            db,
            biochar_record
        )

        await db.commit()

        return BiocharRecordResponse.model_validate(biochar_record)

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create biochar record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create biochar record"
        )


@router.get("/", response_model=list[BiocharRecordResponse])
async def get_biochar_records(
    organization_id: Optional[str] = Query(None),
    feedstock_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get biochar records with pagination and filters."""
    org_id = UUID(organization_id) if organization_id else None

    if not has_permission(current_user.role, "admin:all"):
        org_id = UUID(current_user.organization_id) if current_user.organization_id else None

    biochar_records = await BiocharService.get_biochar_records(
        db,
        organization_id=org_id,
        feedstock_type=feedstock_type,
        skip=skip,
        limit=limit
    )

    return [BiocharRecordResponse.model_validate(b) for b in biochar_records]


@router.get("/{biochar_id}", response_model=BiocharRecordResponse)
async def get_biochar_record(
    biochar_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get biochar record by ID."""
    biochar_record = await BiocharService.get_biochar_record_by_id(db, biochar_id)

    if not biochar_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Biochar record not found"
        )

    return BiocharRecordResponse.model_validate(biochar_record)


@router.post("/calculate", response_model=BiocharCalculationResponse)
async def calculate_biochar_credits(
    calc_request: BiocharCalculationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Calculate carbon credits for biochar without saving."""
    result = formula_engine.calculate_biochar_credit(
        feedstock_quantity=calc_request.feedstock_quantity,
        biochar_yield=calc_request.biochar_yield_percentage,
        carbon_content=calc_request.carbon_content
    )

    return BiocharCalculationResponse(
        formula_code=result.formula_code,
        formula_name=result.formula_name,
        carbon_captured=result.calculation_details.get("carbon_captured_kg", 0),
        soil_improvement_factor=result.emission_factors_used.get("EF_soilimprovement", 0.05),
        total_carbon_credits=result.carbon_credits_generated,
        calculations=result.calculation_details
    )