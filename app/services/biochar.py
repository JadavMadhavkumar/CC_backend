"""
Biochar service for tracking biochar production and soil application.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.formula_engine.base import formula_engine
from app.models.biochar import BiocharRecord
from app.models.organization import Organization
from app.schemas.biochar import BiocharRecordCreate

logger = get_logger(__name__)


class BiocharService:
    """Service for biochar operations."""

    @staticmethod
    async def create_biochar_record(
        db: AsyncSession, biochar_data: BiocharRecordCreate, created_by_id: Optional[UUID] = None
    ) -> BiocharRecord:
        """Create a new biochar record and calculate carbon credits."""
        carbon_captured = (
            biochar_data.biochar_quantity
            * (biochar_data.biochar_yield_percentage / 100)
            * (biochar_data.carbon_content / 100)
            * (44.0 / 12.0)
        )

        biochar_record = BiocharRecord(
            organization_id=UUID(biochar_data.organization_id),
            production_date=biochar_data.production_date,
            feedstock_type=biochar_data.feedstock_type,
            feedstock_quantity=biochar_data.feedstock_quantity,
            feedstock_unit=biochar_data.feedstock_unit,
            biochar_quantity=biochar_data.biochar_quantity,
            biochar_unit=biochar_data.biochar_unit,
            biochar_yield_percentage=biochar_data.biochar_yield_percentage,
            carbon_content=biochar_data.carbon_content,
            carbon_captured=carbon_captured,
            fixed_carbon_percentage=biochar_data.fixed_carbon_percentage,
            volatile_matter_percentage=biochar_data.volatile_matter_percentage,
            ash_percentage=biochar_data.ash_percentage,
            moisture_content=biochar_data.moisture_content,
            pyrolysis_temperature=biochar_data.pyrolysis_temperature,
            pyrolysis_duration=biochar_data.pyrolysis_duration,
            technology=biochar_data.technology,
            application_site=biochar_data.application_site,
            application_area_hectares=biochar_data.application_area_hectares,
            soil_type=biochar_data.soil_type,
            crop_type=biochar_data.crop_type,
            verification_status="pending",
            created_by_id=created_by_id,
        )

        db.add(biochar_record)
        await db.flush()

        calculation_result = formula_engine.calculate_biochar_credit(
            feedstock_quantity=biochar_data.feedstock_quantity,
            biochar_yield=biochar_data.biochar_yield_percentage,
            carbon_content=biochar_data.carbon_content,
        )

        biochar_record.carbon_credit_generated = calculation_result.carbon_credits_generated
        biochar_record.soil_improvement_factor = calculation_result.emission_factors_used.get(
            "EF_soilimprovement", 0.05
        )
        biochar_record.soil_carbon_enhancement = calculation_result.calculation_details.get(
            "soil_carbon_enhancement"
        )
        biochar_record.calculation_formula = calculation_result.formula_code

        org_result = await db.execute(
            select(Organization).where(Organization.id == UUID(biochar_data.organization_id))
        )
        organization = org_result.scalar_one_or_none()

        if organization:
            organization.total_emissions_reduced += calculation_result.emissions_removed

        await db.flush()
        await db.refresh(biochar_record)

        logger.info(
            "Biochar record created",
            biochar_id=str(biochar_record.id),
            carbon_captured=biochar_record.carbon_captured,
            carbon_credits=biochar_record.carbon_credit_generated,
        )

        return biochar_record

    @staticmethod
    async def get_biochar_records(
        db: AsyncSession,
        organization_id: Optional[UUID] = None,
        feedstock_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BiocharRecord]:
        """Get biochar records with filters."""
        query = select(BiocharRecord).where(BiocharRecord.deleted_at.is_(None))

        if organization_id:
            query = query.where(BiocharRecord.organization_id == organization_id)

        if feedstock_type:
            query = query.where(BiocharRecord.feedstock_type == feedstock_type)

        query = query.order_by(BiocharRecord.production_date.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_biochar_record_by_id(
        db: AsyncSession, biochar_id: UUID
    ) -> Optional[BiocharRecord]:
        """Get biochar record by ID."""
        result = await db.execute(
            select(BiocharRecord).where(
                BiocharRecord.id == biochar_id, BiocharRecord.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()


biochar_service = BiocharService()
