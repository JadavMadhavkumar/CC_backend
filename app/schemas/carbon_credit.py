"""
Pydantic schemas for carbon credit management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CarbonCreditBase(BaseModel):
    """Base carbon credit schema."""

    credit_type: str
    category: str
    sub_category: Optional[str] = None
    vintage_year: int
    quantity: float = Field(..., gt=0)
    unit: str = "tCO2e"
    source_type: Optional[str] = None
    waste_type: Optional[str] = None
    processing_method: Optional[str] = None
    methodology: Optional[str] = None
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None


class CarbonCreditCreate(CarbonCreditBase):
    """Carbon credit creation schema."""

    organization_id: str
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    emissions_removed: float = 0


class CarbonCreditUpdate(BaseModel):
    """Carbon credit update schema."""

    status: Optional[str] = None
    verification_level: Optional[str] = None
    verification_id: Optional[str] = None
    verification_date: Optional[datetime] = None
    third_party_verifier: Optional[str] = None
    registry_name: Optional[str] = None
    registry_id: Optional[str] = None
    price_per_credit: Optional[float] = None
    is_retired: Optional[bool] = None
    retirement_reason: Optional[str] = None
    notes: Optional[str] = None


class CarbonCreditInDB(CarbonCreditBase):
    """Carbon credit in database schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    serial_number: str
    status: str
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    emissions_removed: float
    verification_level: str
    verification_id: Optional[str] = None
    verification_date: Optional[datetime] = None
    verification_standard: Optional[str] = None
    blockchain_tx_hash: Optional[str] = None
    is_retired: bool
    created_at: datetime
    updated_at: datetime


class CarbonCreditResponse(CarbonCreditBase):
    """Carbon credit response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    serial_number: str
    quantity: float
    status: str
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    emissions_removed: float
    verification_level: str
    is_retired: bool
    created_at: datetime
    updated_at: datetime


class CarbonCreditTransfer(BaseModel):
    """Carbon credit transfer schema."""

    to_organization_id: str
    quantity: float = Field(..., gt=0)
    price: Optional[float] = None
    currency: str = "USD"
    notes: Optional[str] = None


class CarbonCreditRetire(BaseModel):
    """Carbon credit retirement schema."""

    quantity: float = Field(..., gt=0)
    reason: str


class CarbonCreditStats(BaseModel):
    """Carbon credit statistics schema."""

    total_credits: float
    pending_credits: float
    issued_credits: float
    retired_credits: float
    verified_credits: float
    credits_by_category: dict[str, float]
    credits_by_status: dict[str, float]
