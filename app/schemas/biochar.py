"""
Pydantic schemas for biochar record management.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


class BiocharRecordBase(BaseModel):
    """Base biochar record schema."""

    production_date: datetime
    feedstock_type: str
    feedstock_quantity: float = Field(..., gt=0)
    feedstock_unit: str = "kg"
    biochar_quantity: float = Field(..., gt=0)
    biochar_unit: str = "kg"
    biochar_yield_percentage: float = Field(..., ge=0, le=100)
    carbon_content: float = Field(..., ge=0, le=100)
    fixed_carbon_percentage: Optional[float] = None
    volatile_matter_percentage: Optional[float] = None
    ash_percentage: Optional[float] = None
    moisture_content: Optional[float] = None
    pyrolysis_temperature: Optional[float] = None
    pyrolysis_duration: Optional[float] = None
    technology: Optional[str] = None
    application_site: Optional[str] = None
    application_area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None


class BiocharRecordCreate(BiocharRecordBase):
    """Biochar record creation schema."""

    organization_id: str


class BiocharRecordUpdate(BaseModel):
    """Biochar record update schema."""

    production_date: Optional[datetime] = None
    feedstock_type: Optional[str] = None
    feedstock_quantity: Optional[float] = None
    biochar_quantity: Optional[float] = None
    biochar_yield_percentage: Optional[float] = None
    carbon_content: Optional[float] = None
    pyrolysis_temperature: Optional[float] = None
    technology: Optional[str] = None
    application_site: Optional[str] = None
    is_verified: Optional[bool] = None
    verification_status: Optional[str] = None
    notes: Optional[str] = None


class BiocharRecordInDB(BiocharRecordBase):
    """Biochar record in database schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    carbon_captured: float
    soil_carbon_enhancement: Optional[float] = None
    n2o_reduction: Optional[float] = None
    methane_oxidation: Optional[float] = None
    carbon_credit_generated: float
    soil_improvement_factor: float
    is_verified: bool
    verification_status: str
    verification_id: Optional[str] = None
    calculation_formula: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BiocharRecordResponse(BiocharRecordBase):
    """Biochar record response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    carbon_captured: float
    carbon_credit_generated: float
    is_verified: bool
    verification_status: str
    calculation_formula: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BiocharCalculationRequest(BaseModel):
    """Request schema for biochar carbon credit calculation."""

    feedstock_type: str
    feedstock_quantity: float = Field(..., gt=0)
    feedstock_unit: str = "kg"
    biochar_yield_percentage: float = Field(..., ge=0, le=100)
    carbon_content: float = Field(..., ge=0, le=100)
    apply_soil_improvement: bool = True
    soil_type: Optional[str] = None


class BiocharCalculationResponse(BaseModel):
    """Response schema for biochar carbon credit calculation."""

    formula_code: str
    formula_name: str
    carbon_captured: float
    soil_improvement_factor: float
    total_carbon_credits: float
    unit: str = "tCO2e"
    calculations: dict[str, Any]
