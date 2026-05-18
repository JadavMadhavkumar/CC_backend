"""
Carbon credit model for tracking generated and issued carbon credits.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CarbonCredit(Base):
    """Carbon credit model for tracking generated and issued carbon credits."""

    __tablename__ = "carbon_credits"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, index=True
    )
    credit_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    sub_category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    vintage_year: Mapped[int] = mapped_column(
        nullable=False, index=True
    )
    serial_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    unit: Mapped[str] = mapped_column(
        String(50), nullable=False, default="tCO2e"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )
    source_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    waste_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    processing_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    baseline_emissions: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    project_emissions: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    emissions_reduced: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    emissions_removed: Mapped[float] = mapped_column(
        Numeric(20, 6), default=0, nullable=False
    )
    methodology: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    project_title: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    project_description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    issuance_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expiry_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_level: Mapped[str] = mapped_column(
        String(50), default="unverified", nullable=False
    )
    verification_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True
    )
    verification_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_standard: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    third_party_verifier: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    registry_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    registry_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    blockchain_tx_hash: Mapped[str | None] = mapped_column(
        String(200), nullable=True, index=True
    )
    price_per_credit: Mapped[float | None] = mapped_column(
        Numeric(20, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(10), default="USD", nullable=False
    )
    is_retired: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    retirement_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retirement_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
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
        back_populates="carbon_credits",
        foreign_keys=[organization_id]
    )

    transactions: Mapped[list["CarbonCreditTransaction"]] = relationship(
        "CarbonCreditTransaction",
        back_populates="carbon_credit",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CarbonCredit(id={self.id}, serial_number={self.serial_number}, quantity={self.quantity})>"


class CarbonCreditTransaction(Base):
    """Transaction model for carbon credit transfers."""

    __tablename__ = "carbon_credit_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    carbon_credit_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, index=True
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    from_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )
    to_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    price: Mapped[float | None] = mapped_column(
        Numeric(20, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(10), default="USD", nullable=False
    )
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    carbon_credit: Mapped["CarbonCredit"] = relationship(
        "CarbonCredit",
        back_populates="transactions"
    )

    def __repr__(self) -> str:
        return f"<CarbonCreditTransaction(id={self.id}, type={self.transaction_type}, quantity={self.quantity})>"