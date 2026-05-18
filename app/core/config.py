"""
Core configuration settings for the Carbon Credit Platform.
Loads settings from environment variables with validation.
"""

from typing import Any, Literal
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Carbon Credit Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://carbon_user:carbon_pass@localhost:5432/carbon_credits",
        validation_alias="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    REDIS_CACHE_TTL: int = 300

    # Security
    SECRET_KEY: str = Field(default="changeme-in-production", validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        validation_alias="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        validation_alias="CELERY_RESULT_BACKEND"
    )

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    # Monitoring
    PROMETHEUS_ENABLED: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"

    # Carbon Calculation Defaults
    DEFAULT_CARBON_UNIT: str = "tCO2e"
    DEFAULT_WEIGHT_UNIT: str = "kg"
    DEFAULT_ENERGY_UNIT: str = "kWh"

    # Emission Factors (Defaults - can be overridden by region)
    DEFAULT_GWP_CH4: float = 28.0  # CH4 Global Warming Potential
    DEFAULT_GWP_N2O: float = 265.0  # N2O Global Warming Potential


settings = Settings()


def get_settings() -> Settings:
    return settings


class DatabaseSettings:
    POOL_SIZE = settings.DATABASE_POOL_SIZE
    MAX_OVERFLOW = settings.DATABASE_MAX_OVERFLOW
    ECHO = settings.DATABASE_ECHO


class SecuritySettings:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    PASSWORD_MIN_LENGTH = settings.PASSWORD_MIN_LENGTH


class RedisSettings:
    URL = settings.REDIS_URL
    CACHE_TTL = settings.REDIS_CACHE_TTL