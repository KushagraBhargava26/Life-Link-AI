# backend/app/core/redis.py
# LifeLink AI — Redis Client Factory
# Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
#
# Provides a singleton async Redis client.
# Used for: JWT blacklist, refresh tokens, rate limiting, inventory cache,
# analytics cache, geocode cache, donor search cache.
#
# Phase 1.1: Full Redis client setup — placeholder for actual connection init.

from __future__ import annotations

import structlog
from redis.asyncio import Redis
from redis.asyncio.client import Redis as AsyncRedisClient

from app.config import settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Singleton Redis Client
# ---------------------------------------------------------------------------
_redis_client: AsyncRedisClient | None = None  # type: ignore[type-arg]


def get_redis() -> AsyncRedisClient:  # type: ignore[type-arg]
    """
    Return the singleton async Redis client.

    Raises:
        RuntimeError: If Redis has not been initialized via init_redis().
    """
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call init_redis() at application startup. "
            "Ensure Redis is running and REDIS_URL is set in environment variables."
        )
    return _redis_client


async def init_redis() -> None:
    """
    Initialize the Redis connection at application startup.

    Called from app/main.py lifespan context manager.
    Tests the connection with a PING command to fail fast on misconfiguration.
    """
    global _redis_client
    _redis_client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )

    # Verify connection is alive
    await _redis_client.ping()
    logger.info("Redis connection established", url=settings.REDIS_URL)


async def close_redis() -> None:
    """
    Close the Redis connection at application shutdown.

    Called from app/main.py lifespan context manager.
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed")


# ---------------------------------------------------------------------------
# Redis Key Helpers
# Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
# Key pattern: {version}:{category}:{identifier}
# ---------------------------------------------------------------------------
def make_cache_key(category: str, identifier: str) -> str:
    """
    Build a versioned Redis cache key.

    Architecture: Cache keys include version prefix for easy bulk invalidation.
    Example: v1:inventory:facility_uuid_here

    Args:
        category: Cache category (e.g., 'inventory', 'ratelimit', 'geocode').
        identifier: Unique identifier within the category.

    Returns:
        Formatted Redis key string.
    """
    from app.core.constants import CACHE_KEY_VERSION
    return f"{CACHE_KEY_VERSION}:{category}:{identifier}"


def make_blacklist_key(token_hash: str) -> str:
    """
    Build a Redis key for JWT token blacklisting.

    Architecture: blacklist:{token_hash}
    Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
    """
    return make_cache_key("blacklist", token_hash)


def make_refresh_token_key(user_id: str) -> str:
    """
    Build a Redis key for storing refresh token hashes.

    Architecture: refresh:{user_id}
    Architecture Reference: ARCHITECTURE.md Section 18 (Auth Architecture)
    """
    return make_cache_key("refresh", user_id)


def make_rate_limit_key(ip: str, endpoint: str) -> str:
    """
    Build a Redis key for rate limiting counters.

    Architecture: ratelimit:{ip}:{endpoint}
    Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
    """
    return make_cache_key("ratelimit", f"{ip}:{endpoint}")


def make_inventory_cache_key(facility_id: str) -> str:
    """
    Build a Redis key for inventory caching.

    Architecture: inventory:{facility_id} with TTL=2 minutes
    Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
    """
    return make_cache_key("inventory", facility_id)


def make_geocode_cache_key(address_hash: str) -> str:
    """
    Build a Redis key for geocoded address caching.

    Architecture: geocode:{address_hash} with TTL=24 hours
    Architecture Reference: ARCHITECTURE.md Section 20 (Location Architecture)
    """
    return make_cache_key("geocode", address_hash)


def make_precise_gps_key(donor_id: str) -> str:
    """
    Build a Redis key for temporary precise GPS storage.

    Architecture: Precise GPS stored with TTL<=30 minutes, never in DB.
    Architecture Reference: ARCHITECTURE.md ADR-002 (Donor Location Privacy)
    """
    return make_cache_key("precise_gps", donor_id)
