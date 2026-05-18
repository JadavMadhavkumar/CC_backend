"""
Authentication service for user login, registration, and token management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.logging import get_logger
from app.models.user import User
from app.models.session import UserSession

logger = get_logger(__name__)


class AuthService:
    """Service for handling authentication operations."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "user",
        organization_id: Optional[UUID] = None
    ) -> User:
        """Register a new user."""
        hashed_password = get_password_hash(password)

        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            organization_id=organization_id,
            is_active=True,
            is_verified=False
        )

        db.add(user)
        await db.flush()
        await db.refresh(user)

        logger.info(f"User registered: {email}")
        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user by email and password."""
        result = await db.execute(
            select(User).where(
                User.email == email,
                User.deleted_at.is_(None)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        user.last_login = datetime.now(timezone.utc)
        await db.flush()

        return user

    @staticmethod
    async def create_session(
        db: AsyncSession,
        user: User,
        access_token: str,
        refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a new user session."""
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=30
        )

        session = UserSession(
            user_id=user.id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True
        )

        db.add(session)
        await db.flush()
        await db.refresh(session)

        logger.info(f"Session created for user: {user.email}")
        return session

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str
    ) -> Optional[tuple[str, str]]:
        """Refresh access token using refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            result = await db.execute(
                select(User).where(
                    User.id == UUID(user_id),
                    User.deleted_at.is_(None)
                )
            )
            user = result.scalar_one_or_none()

            if not user or not user.is_active:
                return None

            new_access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role}
            )
            new_refresh_token = create_refresh_token(
                data={"sub": str(user.id), "email": user.email}
            )

            await AuthService.create_session(
                db, user, new_access_token, new_refresh_token
            )

            return new_access_token, new_refresh_token

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    @staticmethod
    async def logout_session(
        db: AsyncSession,
        token: str
    ) -> bool:
        """Logout user by invalidating session."""
        result = await db.execute(
            select(UserSession).where(
                UserSession.token == token,
                UserSession.is_active == True
            )
        )
        session = result.scalar_one_or_none()

        if session:
            session.is_active = False
            await db.flush()
            logger.info(f"Session invalidated for token")
            return True

        return False

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(
            select(User).where(
                User.email == email,
                User.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()


auth_service = AuthService()