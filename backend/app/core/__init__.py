"""Core module for Carbon Credit Platform."""

from app.core.config import settings, get_settings
from app.core.database import Base, get_db, get_db_context, init_db, drop_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    Permission,
    Role,
    ROLE_PERMISSIONS,
    get_role_permissions,
    has_permission,
)
from app.core.logging import configure_logging, get_logger

__all__ = [
    "settings",
    "get_settings",
    "Base",
    "get_db",
    "get_db_context",
    "init_db",
    "drop_db",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "Permission",
    "Role",
    "ROLE_PERMISSIONS",
    "get_role_permissions",
    "has_permission",
    "configure_logging",
    "get_logger",
]