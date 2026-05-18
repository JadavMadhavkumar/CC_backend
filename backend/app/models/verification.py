"""
Verification and audit models for carbon credit verification workflow.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VerificationRequest(Base):
    """Verification request model for carbon credit verification workflow."""

    __tablename__ = "verification_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, index=True
    )
    verification_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20), default="normal", nullable=False
    )
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )
    verified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )
    verification_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    methodology_used: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    verification_standard: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    compliance_score: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    data_accuracy_score: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    completeness_score: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    consistency_score: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    transparency_score: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    issues: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_credits: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    rejected_credits: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="verification_requests",
        foreign_keys=[organization_id]
    )

    def __repr__(self) -> str:
        return f"<VerificationRequest(id={self.id}, entity_type={self.entity_type}, status={self.status})>"


class AuditLog(Base):
    """Audit log model for tracking all system activities."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    entity_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    old_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    request_method: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    request_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    response_status: Mapped[int | None] = mapped_column(nullable=True)
    processing_time_ms: Mapped[float | None] = mapped_column(
        Numeric(20, 2), nullable=True
    )
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True
    )

    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"