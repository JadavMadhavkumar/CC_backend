"""
Pydantic schemas for user authentication and management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)
    organization_id: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[str] = None
    phone_number: Optional[str] = None


class UserInDB(UserBase):
    """User in database schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hashed_password: str
    is_verified: bool
    is_superuser: bool
    organization_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_verified: bool
    is_superuser: bool
    organization_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""

    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class PasswordChange(BaseModel):
    """Password change schema."""

    current_password: str
    new_password: str = Field(..., min_length=8)


class PasswordReset(BaseModel):
    """Password reset schema."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirm schema."""

    token: str
    new_password: str = Field(..., min_length=8)
