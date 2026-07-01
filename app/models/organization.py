"""
Organization model for multi-tenant support.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Organization(Base):
    """Organization model for multi-tenant support."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization_type: Mapped[str] = mapped_column(String(50), nullable=False, default="company")
    registration_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Unknown")
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    primary_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    total_carbon_credits: Mapped[float] = mapped_column(Numeric(20, 4), default=0, nullable=False)
    total_waste_processed: Mapped[float] = mapped_column(Numeric(20, 4), default=0, nullable=False)
    total_emissions_reduced: Mapped[float] = mapped_column(
        Numeric(20, 4), default=0, nullable=False
    )
    verification_level: Mapped[str] = mapped_column(String(50), default="none", nullable=False)
    org_metadata: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
    settings: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", foreign_keys="User.organization_id"
    )

    waste_records: Mapped[list["WasteRecord"]] = relationship(
        "WasteRecord", back_populates="organization", cascade="all, delete-orphan"
    )

    biochar_records: Mapped[list["BiocharRecord"]] = relationship(
        "BiocharRecord", back_populates="organization", cascade="all, delete-orphan"
    )

    carbon_credits: Mapped[list["CarbonCredit"]] = relationship(
        "CarbonCredit", back_populates="organization", cascade="all, delete-orphan"
    )

    emission_records: Mapped[list["EmissionRecord"]] = relationship(
        "EmissionRecord", back_populates="organization", cascade="all, delete-orphan"
    )

    verification_requests: Mapped[list["VerificationRequest"]] = relationship(
        "VerificationRequest", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
