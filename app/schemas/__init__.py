"""Pydantic schemas for API request/response validation."""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    Token,
    TokenData,
    LoginRequest,
    RefreshTokenRequest,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
)

from app.schemas.organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationInDB,
    OrganizationResponse,
    OrganizationStats,
)

from app.schemas.waste import (
    WasteRecordBase,
    WasteRecordCreate,
    WasteRecordUpdate,
    WasteRecordInDB,
    WasteRecordResponse,
    WasteCalculationRequest,
    WasteCalculationResponse,
)

from app.schemas.biochar import (
    BiocharRecordBase,
    BiocharRecordCreate,
    BiocharRecordUpdate,
    BiocharRecordInDB,
    BiocharRecordResponse,
    BiocharCalculationRequest,
    BiocharCalculationResponse,
)

from app.schemas.carbon_credit import (
    CarbonCreditBase,
    CarbonCreditCreate,
    CarbonCreditUpdate,
    CarbonCreditInDB,
    CarbonCreditResponse,
    CarbonCreditTransfer,
    CarbonCreditRetire,
    CarbonCreditStats,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationInDB",
    "OrganizationResponse",
    "OrganizationStats",
    "WasteRecordBase",
    "WasteRecordCreate",
    "WasteRecordUpdate",
    "WasteRecordInDB",
    "WasteRecordResponse",
    "WasteCalculationRequest",
    "WasteCalculationResponse",
    "BiocharRecordBase",
    "BiocharRecordCreate",
    "BiocharRecordUpdate",
    "BiocharRecordInDB",
    "BiocharRecordResponse",
    "BiocharCalculationRequest",
    "BiocharCalculationResponse",
    "CarbonCreditBase",
    "CarbonCreditCreate",
    "CarbonCreditUpdate",
    "CarbonCreditInDB",
    "CarbonCreditResponse",
    "CarbonCreditTransfer",
    "CarbonCreditRetire",
    "CarbonCreditStats",
]
