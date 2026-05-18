"""
Waste management API endpoints for tracking waste collection and processing.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.user import UserResponse
from app.schemas.waste import (
    WasteRecordCreate,
    WasteRecordUpdate,
    WasteRecordResponse,
    WasteCalculationRequest,
    WasteCalculationResponse
)
from app.services.waste import WasteService
from app.services.carbon_credit import CarbonCreditService
from app.formula_engine.base import formula_engine

router = APIRouter(prefix="/waste", tags=["Waste Management"])
logger = get_logger(__name__)


@router.post("/", response_model=WasteRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_waste_record(
    waste_data: WasteRecordCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new waste record with carbon credit calculation."""
    try:
        waste_record = await WasteService.create_waste_record(
            db,
            waste_data,
            created_by_id=UUID(current_user.id)
        )

        carbon_credit = await CarbonCreditService.generate_credit_from_waste(
            db,
            waste_record
        )

        await db.commit()

        return WasteRecordResponse.model_validate(waste_record)

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create waste record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create waste record"
        )


@router.get("/", response_model=list[WasteRecordResponse])
async def get_waste_records(
    organization_id: Optional[str] = Query(None),
    waste_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get waste records with pagination and filters."""
    org_id = UUID(organization_id) if organization_id else None

    if not has_permission(current_user.role, "admin:all"):
        org_id = UUID(current_user.organization_id) if current_user.organization_id else None

    waste_records = await WasteService.get_waste_records(
        db,
        organization_id=org_id,
        waste_type=waste_type,
        skip=skip,
        limit=limit
    )

    return [WasteRecordResponse.model_validate(w) for w in waste_records]


@router.get("/{waste_id}", response_model=WasteRecordResponse)
async def get_waste_record(
    waste_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get waste record by ID."""
    waste_record = await WasteService.get_waste_record_by_id(db, waste_id)

    if not waste_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste record not found"
        )

    return WasteRecordResponse.model_validate(waste_record)


@router.put("/{waste_id}", response_model=WasteRecordResponse)
async def update_waste_record(
    waste_id: UUID,
    waste_data: WasteRecordUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update waste record."""
    update_dict = waste_data.model_dump(exclude_unset=True)

    waste_record = await WasteService.update_waste_record(
        db,
        waste_id,
        **update_dict
    )

    if not waste_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste record not found"
        )

    await db.commit()
    return WasteRecordResponse.model_validate(waste_record)


@router.post("/calculate", response_model=WasteCalculationResponse)
async def calculate_waste_credits(
    calc_request: WasteCalculationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Calculate carbon credits for waste without saving."""
    result = formula_engine.calculate_waste_credit(
        waste_type=calc_request.waste_type,
        plastic_type=calc_request.plastic_type,
        quantity=calc_request.quantity,
        unit=calc_request.unit,
        processing_method=calc_request.processing_method,
        region=calc_request.region
    )

    return WasteCalculationResponse(
        formula_code=result.formula_code,
        formula_name=result.formula_name,
        baseline_emissions=result.baseline_emissions,
        project_emissions=result.project_emissions,
        emissions_reduced=result.emissions_reduced,
        carbon_credits_generated=result.carbon_credits_generated,
        emission_factors_used=result.emission_factors_used
    )