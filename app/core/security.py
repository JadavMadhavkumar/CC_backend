"""
Security utilities including password hashing, JWT token handling,
and role-based access control.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


class Permission:
    """Permission constants for RBAC."""

    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    ORGANIZATION_READ = "organization:read"
    ORGANIZATION_WRITE = "organization:write"
    ORGANIZATION_DELETE = "organization:delete"
    CARBON_CREDIT_READ = "carbon_credit:read"
    CARBON_CREDIT_WRITE = "carbon_credit:write"
    CARBON_CREDIT_VERIFY = "carbon_credit:verify"
    WASTE_READ = "waste:read"
    WASTE_WRITE = "waste:write"
    BIOCHAR_READ = "biochar:read"
    BIOCHAR_WRITE = "biochar:write"
    EMISSION_READ = "emission:read"
    EMISSION_WRITE = "emission:write"
    VERIFICATION_READ = "verification:read"
    VERIFICATION_WRITE = "verification:write"
    VERIFICATION_APPROVE = "verification:approve"
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    ADMIN_ALL = "admin:all"


class Role:
    """Role constants for RBAC."""

    ADMIN = "admin"
    ORGANIZATION_ADMIN = "organization_admin"
    VERIFIER = "verifier"
    USER = "user"
    VIEWER = "viewer"


ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.ADMIN: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.ORGANIZATION_READ,
        Permission.ORGANIZATION_WRITE,
        Permission.ORGANIZATION_DELETE,
        Permission.CARBON_CREDIT_READ,
        Permission.CARBON_CREDIT_WRITE,
        Permission.CARBON_CREDIT_VERIFY,
        Permission.WASTE_READ,
        Permission.WASTE_WRITE,
        Permission.BIOCHAR_READ,
        Permission.BIOCHAR_WRITE,
        Permission.EMISSION_READ,
        Permission.EMISSION_WRITE,
        Permission.VERIFICATION_READ,
        Permission.VERIFICATION_WRITE,
        Permission.VERIFICATION_APPROVE,
        Permission.REPORT_READ,
        Permission.REPORT_WRITE,
        Permission.ADMIN_ALL,
    },
    Role.ORGANIZATION_ADMIN: {
        Permission.ORGANIZATION_READ,
        Permission.ORGANIZATION_WRITE,
        Permission.CARBON_CREDIT_READ,
        Permission.CARBON_CREDIT_WRITE,
        Permission.WASTE_READ,
        Permission.WASTE_WRITE,
        Permission.BIOCHAR_READ,
        Permission.BIOCHAR_WRITE,
        Permission.EMISSION_READ,
        Permission.EMISSION_WRITE,
        Permission.REPORT_READ,
        Permission.REPORT_WRITE,
    },
    Role.VERIFIER: {
        Permission.CARBON_CREDIT_READ,
        Permission.CARBON_CREDIT_VERIFY,
        Permission.WASTE_READ,
        Permission.BIOCHAR_READ,
        Permission.EMISSION_READ,
        Permission.VERIFICATION_READ,
        Permission.VERIFICATION_WRITE,
        Permission.VERIFICATION_APPROVE,
        Permission.REPORT_READ,
    },
    Role.USER: {
        Permission.CARBON_CREDIT_READ,
        Permission.CARBON_CREDIT_WRITE,
        Permission.WASTE_READ,
        Permission.WASTE_WRITE,
        Permission.BIOCHAR_READ,
        Permission.BIOCHAR_WRITE,
        Permission.EMISSION_READ,
        Permission.EMISSION_WRITE,
        Permission.REPORT_READ,
    },
    Role.VIEWER: {
        Permission.CARBON_CREDIT_READ,
        Permission.WASTE_READ,
        Permission.BIOCHAR_READ,
        Permission.EMISSION_READ,
        Permission.REPORT_READ,
    },
}


def get_role_permissions(role: str) -> set[str]:
    """Get permissions for a role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_role_permissions(role)
