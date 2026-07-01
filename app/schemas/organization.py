"""
Pydantic schemas for organization management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    organization_type: str = "company"
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Unknown"
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Organization creation schema."""

    pass


class OrganizationUpdate(BaseModel):
    """Organization update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    is_verified: Optional[bool] = None
    verification_level: Optional[str] = None


class OrganizationInDB(OrganizationBase):
    """Organization in database schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_verified: bool
    total_carbon_credits: float
    total_waste_processed: float
    total_emissions_reduced: float
    verification_level: str
    created_at: datetime
    updated_at: datetime


class OrganizationResponse(OrganizationBase):
    """Organization response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_verified: bool
    total_carbon_credits: float
    total_waste_processed: float
    total_emissions_reduced: float
    verification_level: str
    created_at: datetime
    updated_at: datetime


class OrganizationStats(BaseModel):
    """Organization statistics schema."""

    total_carbon_credits: float
    total_waste_processed: float
    total_emissions_reduced: float
    waste_records_count: int
    biochar_records_count: int
    carbon_credits_count: int
    pending_verifications: int
