"""
Verification service for carbon credit verification workflow.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.verification import VerificationRequest
from app.models.waste import WasteRecord
from app.models.biochar import BiocharRecord
from app.models.carbon_credit import CarbonCredit

logger = get_logger(__name__)


class VerificationService:
    """Service for verification operations."""

    @staticmethod
    async def create_verification_request(
        db: AsyncSession,
        organization_id: UUID,
        entity_type: str,
        entity_id: UUID,
        verification_type: str,
        priority: str = "normal",
    ) -> VerificationRequest:
        """Create a new verification request."""
        verification = VerificationRequest(
            organization_id=organization_id,
            entity_type=entity_type,
            entity_id=entity_id,
            verification_type=verification_type,
            priority=priority,
            status="pending",
        )

        db.add(verification)
        await db.flush()
        await db.refresh(verification)

        logger.info(f"Verification request created: {verification.id}")
        return verification

    @staticmethod
    async def get_verification_requests(
        db: AsyncSession,
        organization_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[VerificationRequest]:
        """Get verification requests with filters."""
        query = select(VerificationRequest)

        if organization_id:
            query = query.where(VerificationRequest.organization_id == organization_id)

        if status:
            query = query.where(VerificationRequest.status == status)

        query = query.order_by(VerificationRequest.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_verification_request_by_id(
        db: AsyncSession, verification_id: UUID
    ) -> Optional[VerificationRequest]:
        """Get verification request by ID."""
        result = await db.execute(
            select(VerificationRequest).where(VerificationRequest.id == verification_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def approve_verification(
        db: AsyncSession,
        verification_id: UUID,
        verified_by: UUID,
        compliance_score: float,
        data_accuracy_score: float,
        completeness_score: float,
        conclusions: str,
        approved_credits: float,
    ) -> Optional[VerificationRequest]:
        """Approve a verification request."""
        verification = await VerificationService.get_verification_request_by_id(db, verification_id)

        if not verification:
            return None

        verification.status = "approved"
        verification.verified_by_id = verified_by
        verification.verification_date = datetime.now(timezone.utc)
        verification.compliance_score = compliance_score
        verification.data_accuracy_score = data_accuracy_score
        verification.completeness_score = completeness_score
        verification.conclusion = conclusions
        verification.approved_credits = approved_credits
        verification.completed_at = datetime.now(timezone.utc)

        await VerificationService._update_entity_verification(
            db, verification.entity_type, verification.entity_id, verification_id
        )

        await db.flush()
        await db.refresh(verification)

        logger.info(f"Verification approved: {verification_id}")
        return verification

    @staticmethod
    async def reject_verification(
        db: AsyncSession,
        verification_id: UUID,
        verified_by: UUID,
        findings: str,
        rejected_credits: float,
    ) -> Optional[VerificationRequest]:
        """Reject a verification request."""
        verification = await VerificationService.get_verification_request_by_id(db, verification_id)

        if not verification:
            return None

        verification.status = "rejected"
        verification.verified_by_id = verified_by
        verification.verification_date = datetime.now(timezone.utc)
        verification.findings = findings
        verification.rejected_credits = rejected_credits
        verification.completed_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(verification)

        logger.info(f"Verification rejected: {verification_id}")
        return verification

    @staticmethod
    async def _update_entity_verification(
        db: AsyncSession, entity_type: str, entity_id: UUID, verification_id: UUID
    ) -> None:
        """Update the entity's verification status."""
        if entity_type == "waste":
            result = await db.execute(select(WasteRecord).where(WasteRecord.id == entity_id))
            entity = result.scalar_one_or_none()
            if entity:
                entity.is_verified = True
                entity.verification_status = "verified"
                entity.verification_id = verification_id

        elif entity_type == "biochar":
            result = await db.execute(select(BiocharRecord).where(BiocharRecord.id == entity_id))
            entity = result.scalar_one_or_none()
            if entity:
                entity.is_verified = True
                entity.verification_status = "verified"
                entity.verification_id = verification_id

        elif entity_type == "carbon_credit":
            result = await db.execute(select(CarbonCredit).where(CarbonCredit.id == entity_id))
            entity = result.scalar_one_or_none()
            if entity:
                entity.verification_level = "verified"
                entity.verification_id = verification_id
                entity.verification_date = datetime.now(timezone.utc)


verification_service = VerificationService()
