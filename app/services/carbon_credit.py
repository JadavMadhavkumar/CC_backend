"""
Carbon Credit service for managing carbon credit operations.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.formula_engine.base import formula_engine, CalculationInput
from app.models.carbon_credit import CarbonCredit
from app.models.waste import WasteRecord
from app.models.biochar import BiocharRecord
from app.models.organization import Organization
from app.schemas.carbon_credit import CarbonCreditCreate

logger = get_logger(__name__)


class CarbonCreditService:
    """Service for carbon credit operations."""

    @staticmethod
    async def generate_credit_from_waste(
        db: AsyncSession,
        waste_record: WasteRecord
    ) -> CarbonCredit:
        """Generate carbon credit from waste record."""
        calculation_result = formula_engine.calculate_waste_credit(
            waste_type=waste_record.waste_type,
            plastic_type=waste_record.plastic_type,
            quantity=waste_record.quantity,
            unit=waste_record.unit,
            processing_method=waste_record.processing_method
        )

        serial_number = f"CC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        carbon_credit = CarbonCredit(
            organization_id=waste_record.organization_id,
            credit_type="waste_management",
            category=waste_record.waste_type,
            sub_category=waste_record.plastic_type,
            vintage_year=datetime.now().year,
            serial_number=serial_number,
            quantity=calculation_result.carbon_credits_generated,
            unit="tCO2e",
            status="generated",
            waste_type=waste_record.waste_type,
            processing_method=waste_record.processing_method,
            baseline_emissions=calculation_result.baseline_emissions,
            project_emissions=calculation_result.project_emissions,
            emissions_reduced=calculation_result.emissions_reduced,
            start_date=waste_record.collection_date,
            verification_status="pending"
        )

        db.add(carbon_credit)

        waste_record.carbon_credit_generated = calculation_result.carbon_credits_generated
        waste_record.calculation_formula = calculation_result.formula_code
        waste_record.baseline_emissions = calculation_result.baseline_emissions
        waste_record.project_emissions = calculation_result.project_emissions
        waste_record.emissions_reduced = calculation_result.emissions_reduced

        await db.flush()
        await db.refresh(carbon_credit)

        logger.info(
            f"Carbon credit generated from waste: {serial_number}",
            quantity=carbon_credit.quantity
        )

        return carbon_credit

    @staticmethod
    async def generate_credit_from_biochar(
        db: AsyncSession,
        biochar_record: BiocharRecord
    ) -> CarbonCredit:
        """Generate carbon credit from biochar record."""
        calculation_result = formula_engine.calculate_biochar_credit(
            feedstock_quantity=biochar_record.feedstock_quantity,
            biochar_yield=biochar_record.biochar_yield_percentage,
            carbon_content=biochar_record.carbon_content
        )

        serial_number = f"BC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        carbon_credit = CarbonCredit(
            organization_id=biochar_record.organization_id,
            credit_type="biochar",
            category="soil_carbon",
            vintage_year=datetime.now().year,
            serial_number=serial_number,
            quantity=calculation_result.carbon_credits_generated,
            unit="tCO2e",
            status="generated",
            baseline_emissions=calculation_result.baseline_emissions,
            project_emissions=calculation_result.project_emissions,
            emissions_reduced=calculation_result.emissions_reduced,
            emissions_removed=calculation_result.emissions_removed,
            start_date=biochar_record.production_date,
            verification_status="pending"
        )

        db.add(carbon_credit)

        biochar_record.carbon_credit_generated = calculation_result.carbon_credits_generated
        biochar_record.soil_improvement_factor = calculation_result.emission_factors_used.get("EF_soilimprovement", 0.05)
        biochar_record.carbon_captured = calculation_result.calculation_details.get("carbon_captured_kg", 0)
        biochar_record.calculation_formula = calculation_result.formula_code

        await db.flush()
        await db.refresh(carbon_credit)

        logger.info(
            f"Carbon credit generated from biochar: {serial_number}",
            quantity=carbon_credit.quantity
        )

        return carbon_credit

    @staticmethod
    async def get_credits_by_organization(
        db: AsyncSession,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[CarbonCredit]:
        """Get carbon credits by organization."""
        result = await db.execute(
            select(CarbonCredit)
            .where(
                CarbonCredit.organization_id == organization_id,
                CarbonCredit.deleted_at.is_(None)
            )
            .order_by(CarbonCredit.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_credit_by_id(
        db: AsyncSession,
        credit_id: UUID
    ) -> Optional[CarbonCredit]:
        """Get carbon credit by ID."""
        result = await db.execute(
            select(CarbonCredit).where(
                CarbonCredit.id == credit_id,
                CarbonCredit.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_credit_by_serial(
        db: AsyncSession,
        serial_number: str
    ) -> Optional[CarbonCredit]:
        """Get carbon credit by serial number."""
        result = await db.execute(
            select(CarbonCredit).where(
                CarbonCredit.serial_number == serial_number,
                CarbonCredit.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def retire_credit(
        db: AsyncSession,
        credit_id: UUID,
        reason: str
    ) -> Optional[CarbonCredit]:
        """Retire carbon credit."""
        credit = await CarbonCreditService.get_credit_by_id(db, credit_id)
        if not credit:
            return None

        credit.is_retired = True
        credit.retirement_date = datetime.now(timezone.utc)
        credit.retirement_reason = reason
        credit.status = "retired"

        await db.flush()
        await db.refresh(credit)

        logger.info(f"Carbon credit retired: {credit.serial_number}", reason=reason)
        return credit

    @staticmethod
    async def update_organization_stats(
        db: AsyncSession,
        organization_id: UUID
    ) -> None:
        """Update organization carbon credit statistics."""
        result = await db.execute(
            select(
                func.sum(CarbonCredit.quantity),
                func.count(CarbonCredit.id)
            )
            .where(
                CarbonCredit.organization_id == organization_id,
                CarbonCredit.deleted_at.is_(None),
                CarbonCredit.status == "issued"
            )
        )
        total_credits, credits_count = result.one()

        org_result = await db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        organization = org_result.scalar_one_or_none()

        if organization:
            organization.total_carbon_credits = total_credits or 0
            await db.flush()

        logger.info(
            f"Organization stats updated",
            org_id=str(organization_id),
            total_credits=total_credits
        )


carbon_credit_service = CarbonCreditService()