"""
Biochar record model for tracking biochar production and application.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BiocharRecord(Base):
    """Biochar record model for tracking biochar production and application."""

    __tablename__ = "biochar_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id"), nullable=False, index=True
    )
    production_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    feedstock_type: Mapped[str] = mapped_column(String(100), nullable=False)
    feedstock_quantity: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    feedstock_unit: Mapped[str] = mapped_column(String(50), nullable=False, default="kg")
    biochar_quantity: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    biochar_unit: Mapped[str] = mapped_column(String(50), nullable=False, default="kg")
    biochar_yield_percentage: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    carbon_content: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    carbon_captured: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    fixed_carbon_percentage: Mapped[float] = mapped_column(Numeric(10, 4), nullable=True)
    volatile_matter_percentage: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    ash_percentage: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    moisture_content: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    pyrolysis_temperature: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pyrolysis_duration: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    technology: Mapped[str | None] = mapped_column(String(100), nullable=True)
    application_site: Mapped[str | None] = mapped_column(String(255), nullable=True)
    application_area_hectares: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    crop_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    soil_carbon_enhancement: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    n2o_reduction: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    methane_oxidation: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    carbon_credit_generated: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    soil_improvement_factor: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    calculation_formula: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    verification_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    biochar_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
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
        "Organization", back_populates="biochar_records", foreign_keys=[organization_id]
    )

    def __repr__(self) -> str:
        return (
            f"<BiocharRecord(id={self.id}, biochar_quantity={self.biochar_quantity}"
            f", carbon_captured={self.carbon_captured})>"
        )
