"""
Waste record model for tracking waste collection and processing.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WasteRecord(Base):
    """Waste record model for tracking waste collection and processing."""

    __tablename__ = "waste_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False, index=True
    )
    waste_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    plastic_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    collection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    quantity: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="kg")
    moisture_content: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    calorific_value: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    processing_method: Mapped[str] = mapped_column(String(100), nullable=False)
    processing_facility: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(12, 8), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(12, 8), nullable=True)
    carbon_credit_generated: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    emission_factor_used: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    calculation_formula: Mapped[str | None] = mapped_column(String(100), nullable=True)
    baseline_emissions: Mapped[float] = mapped_column(Numeric(20, 6), default=0, nullable=False)
    project_emissions: Mapped[float] = mapped_column(Numeric(20, 6), default=0, nullable=False)
    emissions_reduced: Mapped[float] = mapped_column(Numeric(20, 6), default=0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    verification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    waste_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="waste_records", foreign_keys=[organization_id]
    )

    def __repr__(self) -> str:
        return (
            f"<WasteRecord(id={self.id}, waste_type={self.waste_type}, quantity={self.quantity})>"
        )
