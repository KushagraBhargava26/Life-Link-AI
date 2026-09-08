# ai/app/config.py
# LifeLink AI — AI Service Configuration via pydantic-settings
# Architecture Reference: ARCHITECTURE.md Section 17 & Section 29
#
# All configuration comes from environment variables.

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """
    AI Service settings loaded from environment variables.
    Validated by Pydantic on startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: Literal["development", "production", "test"] = Field(
        default="development",
        description="Application environment: development | production | test",
    )
    APP_NAME: str = Field(default="LifeLink AI Service")
    APP_VERSION: str = Field(default="1.0.0-alpha")

    # API key for internal backend-to-AI-service authorization
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

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log level. Use DEBUG only in development.",
    )

    @property
    def IS_PRODUCTION(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def IS_DEVELOPMENT(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache(maxsize=1)
def get_ai_settings() -> AISettings:
    return AISettings()  # type: ignore[call-arg]


ai_settings = get_ai_settings()
