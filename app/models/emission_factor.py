"""
Emission factor model for storing configurable carbon emission factors
by region, material type, and disposal method.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmissionFactor(Base):
    """Emission factor model for storing configurable carbon emission factors."""

    __tablename__ = "emission_factors"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    sub_category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    material_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    disposal_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    region: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    factor_value: Mapped[float] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    unit: Mapped[str] = mapped_column(
        String(50), nullable=False, default="kgCO2e/unit"
    )
    factor_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="emission"
    )
    source: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    source_year: Mapped[int | None] = mapped_column(nullable=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    uncertainty: Mapped[float | None] = mapped_column(
        Numeric(10, 4), nullable=True
    )
    methodology: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )

    def __repr__(self) -> str:
        return f"<EmissionFactor(id={self.id}, code={self.code}, factor_value={self.factor_value})>"


class GWPFactor(Base):
    """Global Warming Potential factors for different greenhouse gases."""

    __tablename__ = "gwp_factors"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    gas_type: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    gwp_value_100yr: Mapped[float] = mapped_column(
        Numeric(20, 4), nullable=False
    )
    gwp_value_20yr: Mapped[float | None] = mapped_column(
        Numeric(20, 4), nullable=True
    )
    gwp_value_500yr: Mapped[float | None] = mapped_column(
        Numeric(20, 4), nullable=True
    )
    source: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    source_year: Mapped[int | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<GWPFactor(gas_type={self.gas_type}, gwp_value={self.gwp_value_100yr})>"