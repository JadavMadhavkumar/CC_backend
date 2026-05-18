"""
Pydantic schemas for waste record management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class WasteRecordBase(BaseModel):
    """Base waste record schema."""
    waste_type: str
    plastic_type: Optional[str] = None
    source: str
    collection_date: datetime
    quantity: float = Field(..., gt=0)
    unit: str = "kg"
    moisture_content: Optional[float] = None
    calorific_value: Optional[float] = None
    processing_method: str
    processing_facility: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class WasteRecordCreate(WasteRecordBase):
    """Waste record creation schema."""
    organization_id: str


class WasteRecordUpdate(BaseModel):
    """Waste record update schema."""
    waste_type: Optional[str] = None
    plastic_type: Optional[str] = None
    source: Optional[str] = None
    collection_date: Optional[datetime] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    moisture_content: Optional[float] = None
    calorific_value: Optional[float] = None
    processing_method: Optional[str] = None
    processing_facility: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_verified: Optional[bool] = None
    verification_status: Optional[str] = None
    notes: Optional[str] = None


class WasteRecordInDB(WasteRecordBase):
    """Waste record in database schema."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    carbon_credit_generated: float
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    is_verified: bool
    verification_status: str
    verification_id: Optional[str] = None
    calculation_formula: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WasteRecordResponse(WasteRecordBase):
    """Waste record response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    carbon_credit_generated: float
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    is_verified: bool
    verification_status: str
    calculation_formula: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WasteCalculationRequest(BaseModel):
    """Request schema for waste carbon credit calculation."""
    waste_type: str
    plastic_type: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit: str = "kg"
    processing_method: str
    region: Optional[str] = None
    disposal_method_baseline: str
    disposal_method_project: str


class WasteCalculationResponse(BaseModel):
    """Response schema for waste carbon credit calculation."""
    formula_code: str
    formula_name: str
    baseline_emissions: float
    project_emissions: float
    emissions_reduced: float
    carbon_credits_generated: float
    unit: str = "tCO2e"
    emission_factors_used: dict[str, float]