"""
Emission record model for tracking baseline and project emissions.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmissionRecord(Base):
    """Emission record model for tracking baseline and project emissions."""

    __tablename__ = "emission_records"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, index=True
    )
    emission_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    sub_category: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    source: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    reporting_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    reporting_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scope: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    activity_data: Mapped[float] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    activity_unit: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    emission_factor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )
    emission_factor_value: Mapped[float | None] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    emission_factor_unit: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    emissions_co2e: Mapped[float] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    emissions_co2: Mapped[float | None] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    emissions_ch4: Mapped[float | None] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    emissions_n2o: Mapped[float | None] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    baseline_emissions: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    project_emissions: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    net_emissions: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    carbon_offsets_used: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    verification_status: Mapped[str] = mapped_column(
        String(50), default="unverified", nullable=False
    )
    verification_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )
    methodology: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    uncertainty: Mapped[float | None] = mapped_column(
        Numeric(10, 4), nullable=True
    )
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="emission_records",
        foreign_keys=[organization_id]
    )

    def __repr__(self) -> str:
        return f"<EmissionRecord(id={self.id}, emission_type={self.emission_type}, emissions_co2e={self.emissions_co2e})>"