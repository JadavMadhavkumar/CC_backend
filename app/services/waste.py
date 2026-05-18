"""
Waste management service for tracking waste collection and processing.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.formula_engine.base import formula_engine
from app.models.waste import WasteRecord
from app.models.organization import Organization
from app.schemas.waste import WasteRecordCreate

logger = get_logger(__name__)


class WasteService:
    """Service for waste management operations."""

    @staticmethod
    async def create_waste_record(
        db: AsyncSession,
        waste_data: WasteRecordCreate,
        created_by_id: Optional[UUID] = None
    ) -> WasteRecord:
        """Create a new waste record and calculate carbon credits."""
        waste_record = WasteRecord(
            organization_id=UUID(waste_data.organization_id),
            waste_type=waste_data.waste_type,
            plastic_type=waste_data.plastic_type,
            source=waste_data.source,
            collection_date=waste_data.collection_date,
            quantity=waste_data.quantity,
            unit=waste_data.unit,
            moisture_content=waste_data.moisture_content,
            calorific_value=waste_data.calorific_value,
            processing_method=waste_data.processing_method,
            processing_facility=waste_data.processing_facility,
            location=waste_data.location,
            latitude=waste_data.latitude,
            longitude=waste_data.longitude,
            verification_status="pending",
            created_by_id=created_by_id
        )

        db.add(waste_record)
        await db.flush()

        calculation_result = formula_engine.calculate_waste_credit(
            waste_type=waste_data.waste_type,
            plastic_type=waste_data.plastic_type,
            quantity=waste_data.quantity,
            unit=waste_data.unit,
            processing_method=waste_data.processing_method
        )

        waste_record.carbon_credit_generated = calculation_result.carbon_credits_generated
        waste_record.calculation_formula = calculation_result.formula_code
        waste_record.baseline_emissions = calculation_result.baseline_emissions
        waste_record.project_emissions = calculation_result.project_emissions
        waste_record.emissions_reduced = calculation_result.emissions_reduced

        org_result = await db.execute(
            select(Organization).where(Organization.id == UUID(waste_data.organization_id))
        )
        organization = org_result.scalar_one_or_none()

        if organization:
            organization.total_waste_processed += waste_data.quantity
            organization.total_emissions_reduced += calculation_result.emissions_reduced

        await db.flush()
        await db.refresh(waste_record)

        logger.info(
            f"Waste record created",
            waste_id=str(waste_record.id),
            quantity=waste_record.quantity,
            carbon_credits=waste_record.carbon_credit_generated
        )

        return waste_record

    @staticmethod
    async def get_waste_records(
        db: AsyncSession,
        organization_id: Optional[UUID] = None,
        waste_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[WasteRecord]:
        """Get waste records with filters."""
        query = select(WasteRecord).where(WasteRecord.deleted_at.is_(None))

        if organization_id:
            query = query.where(WasteRecord.organization_id == organization_id)

        if waste_type:
            query = query.where(WasteRecord.waste_type == waste_type)

        query = query.order_by(WasteRecord.collection_date.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_waste_record_by_id(
        db: AsyncSession,
        waste_id: UUID
    ) -> Optional[WasteRecord]:
        """Get waste record by ID."""
        result = await db.execute(
            select(WasteRecord).where(
                WasteRecord.id == waste_id,
                WasteRecord.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_waste_record(
        db: AsyncSession,
        waste_id: UUID,
        **update_fields
    ) -> Optional[WasteRecord]:
        """Update waste record."""
        waste_record = await WasteService.get_waste_record_by_id(db, waste_id)
        if not waste_record:
            return None

        for key, value in update_fields.items():
            if value is not None and hasattr(waste_record, key):
                setattr(waste_record, key, value)

        waste_record.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(waste_record)

        logger.info(f"Waste record updated: {waste_id}")
        return waste_record

    @staticmethod
    async def verify_waste_record(
        db: AsyncSession,
        waste_id: UUID,
        verification_id: UUID,
        verified_by: UUID
    ) -> Optional[WasteRecord]:
        """Verify waste record."""
        waste_record = await WasteService.get_waste_record_by_id(db, waste_id)
        if not waste_record:
            return None

        waste_record.is_verified = True
        waste_record.verification_status = "verified"
        waste_record.verification_id = verification_id
        waste_record.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(waste_record)

        logger.info(f"Waste record verified: {waste_id}")
        return waste_record


waste_service = WasteService()