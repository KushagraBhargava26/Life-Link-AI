# backend/app/config.py
# LifeLink AI — Application Configuration via pydantic-settings
# Architecture Reference: ARCHITECTURE.md Section 29 (Environment Variables Reference)
#
# All configuration comes from environment variables — no hardcoded secrets.
# Rule from ARCHITECTURE.md Section 30:
# "All configuration comes from environment variables — no hardcoded secrets or URLs."

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All values are validated by Pydantic on startup.
    If a required variable is missing, the application will fail fast
    with a clear error message — never with a runtime crash deep inside the code.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore unknown env vars
    )

    # =========================================================================
    # Application Identity
    # =========================================================================
    APP_ENV: Literal["development", "production", "test"] = Field(
        default="development",
        description="Application environment: development | production | test",
    )
    APP_NAME: str = Field(default="LifeLink AI")
    APP_VERSION: str = Field(default="1.0.0-alpha")

    # =========================================================================
    # Security — JWT
    # Architecture Reference: ARCHITECTURE.md Section 18 (Authentication Architecture)
    # =========================================================================
    SECRET_KEY: str = Field(
        description="256-bit secret key for JWT signing. Generate with: python -c \"import secrets; print(secrets.token_hex(32))\"",
    )
    ACCESS_TOKEN_TTL: int = Field(
        default=900,
        description="Access token TTL in seconds. Default: 15 minutes.",
    )
    REFRESH_TOKEN_TTL: int = Field(
        default=604800,
        description="Refresh token TTL in seconds. Default: 7 days.",
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm. HS256 as per ARCHITECTURE.md Section 18.",
    )

    # =========================================================================
    # Database — PostgreSQL
    # Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
    # =========================================================================
    DATABASE_URL: str = Field(
        description="Async PostgreSQL connection URL. Format: postgresql+asyncpg://user:pass@host:port/dbname",
    )
    DB_POOL_MIN: int = Field(default=5, description="Minimum DB connection pool size.")
    DB_POOL_MAX: int = Field(default=20, description="Maximum DB connection pool size.")

    # =========================================================================
    # Cache — Redis
    # Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
    # =========================================================================
    REDIS_URL: str = Field(
        description="Redis connection URL. Format: redis://host:port/db",
    )

    # =========================================================================
    # AI Service
    # Architecture Reference: ARCHITECTURE.md Section 17 (AI Architecture)
    # =========================================================================
    AI_SERVICE_URL: AnyHttpUrl = Field(
        default="http://localhost:8001",  # type: ignore[assignment]
        description="Internal URL of the AI FastAPI service. In Docker: http://ai-service:8001",
    )
    AI_SERVICE_API_KEY: str = Field(
        description="Internal API key for authenticating backend-to-AI-service requests.",
    )
    AI_MATCHING_TIMEOUT_SECONDS: int = Field(
        default=5,
        description="Timeout for AI matching requests in seconds.",
    )
    AI_MAX_DONORS_PER_MATCH: int = Field(
        default=10,
        description="Maximum number of donors returned per match result.",
    )
    AI_DEFAULT_SEARCH_RADIUS_KM: float = Field(
        default=50.0,
        description="Default donor search radius in kilometers.",
    )

    # =========================================================================
    # Firebase — Push Notifications
    # Architecture Reference: ARCHITECTURE.md Section 19 (Notification Architecture)
    # =========================================================================
    FIREBASE_CREDENTIALS_JSON: str = Field(
        default="",
        description="Base64-encoded Firebase service account JSON.",
    )

    # =========================================================================
    # Email — SMTP
    # =========================================================================
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM_NAME: str = Field(default="LifeLink AI")
    SMTP_FROM_EMAIL: str = Field(default="")

    # =========================================================================
    # Maps and Geocoding
    # Architecture Reference: ARCHITECTURE.md Section 20 (Maps and Location Architecture)
    # =========================================================================
    NOMINATIM_BASE_URL: AnyHttpUrl = Field(
        default="https://nominatim.openstreetmap.org",  # type: ignore[assignment]
        description="Nominatim geocoding service base URL.",
    )
    GOOGLE_MAPS_API_KEY: str = Field(
        default="",
        description="Google Maps API key. Leave empty to use OpenStreetMap (default).",
    )

    # =========================================================================
    # Frontend
    # =========================================================================
    NEXT_PUBLIC_API_BASE_URL: str = Field(default="http://localhost/api/v1")
    NEXT_PUBLIC_APP_NAME: str = Field(default="LifeLink AI")
    NEXT_PUBLIC_APP_VERSION: str = Field(default="1.0.0")

    # =========================================================================
    # CORS
    # =========================================================================
    CORS_ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins.",
    )

    # =========================================================================
    # Rate Limiting
    # Architecture Reference: ARCHITECTURE.md Section 16 (Rate Limiting Middleware)
    # =========================================================================
    RATE_LIMIT_GENERAL: int = Field(
        default=100,
        description="General rate limit: requests per minute per IP.",
    )
    RATE_LIMIT_LOGIN: int = Field(
        default=5,
        description="Login rate limit: failed attempts per 15 min per IP.",
    )
    RATE_LIMIT_REGISTER: int = Field(
        default=10,
        description="Registration rate limit: registrations per hour per IP.",
    )

    # =========================================================================
    # Logging
    # =========================================================================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log level. Use DEBUG only in development.",
    )

    # =========================================================================
    # Deployment (Production Only)
    # =========================================================================
    DOMAIN: str = Field(default="localhost")
    SSL_CERT_PATH: str = Field(default="")
    SSL_KEY_PATH: str = Field(default="")

    # =========================================================================
    # Computed Fields (derived from base settings)
    # =========================================================================
    @computed_field  # type: ignore[misc]
    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]

    @computed_field  # type: ignore[misc]
    @property
    def IS_PRODUCTION(self) -> bool:
        """True if running in production environment."""
        return self.APP_ENV == "production"

    @computed_field  # type: ignore[misc]
    @property
    def IS_DEVELOPMENT(self) -> bool:
        """True if running in development environment."""
        return self.APP_ENV == "development"

    # =========================================================================
    # Validators
    # =========================================================================
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key meets minimum security requirements."""
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if v == "<REPLACE_WITH_256_BIT_SECRET>":
            raise ValueError(
                "SECRET_KEY must be changed from the default placeholder. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses the asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use the asyncpg driver. "
                "Format: postgresql+asyncpg://user:pass@host:port/dbname"
            )
        return v


# ---------------------------------------------------------------------------
# Cached settings instance
# lru_cache ensures Settings() is only instantiated once per process.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Module-level settings instance
# Import this in all other modules: from app.config import settings
# ---------------------------------------------------------------------------
settings = get_settings()
