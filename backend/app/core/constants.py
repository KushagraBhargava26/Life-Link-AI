# backend/app/core/constants.py
# LifeLink AI — Application-Wide Constants
# Architecture Reference: ARCHITECTURE.md Section 31 (Coding Standards)
#
# Rule: Constants defined in UPPER_SNAKE_CASE in core/constants.py.
# Never hardcode these values in business logic modules.
#
# Phase 1.1: Constants defined. No business logic references yet.

from __future__ import annotations

# =============================================================================
# Blood Type Constants
# Architecture Reference: ARCHITECTURE.md ADR-003 (Blood Group Data Model)
# ABO stored as ENUM, Rh as BOOLEAN
# =============================================================================

# Valid ABO blood group values (PostgreSQL ENUM in Phase 1.2)
VALID_ABO_GROUPS: frozenset[str] = frozenset({"A", "B", "AB", "O"})

# Display string mapping: (abo_group, rh_positive) → display string
BLOOD_TYPE_DISPLAY: dict[tuple[str, bool], str] = {
    ("A", True): "A+",
    ("A", False): "A-",
    ("B", True): "B+",
    ("B", False): "B-",
    ("AB", True): "AB+",
    ("AB", False): "AB-",
    ("O", True): "O+",
    ("O", False): "O-",
}

# Blood compatibility matrix
# Architecture Reference: ARCHITECTURE.md Section 32 (Blood Compatibility Matrix)
# Maps donor ABO group → set of compatible recipient ABO groups
ABO_COMPATIBILITY: dict[str, frozenset[str]] = {
    "O": frozenset({"O", "A", "B", "AB"}),   # O is universal donor
    "A": frozenset({"A", "AB"}),
    "B": frozenset({"B", "AB"}),
    "AB": frozenset({"AB"}),                   # AB can only donate to AB
}

# =============================================================================
# Donation Constants
# Architecture Reference: ARCHITECTURE.md Section 33 (Donor Workflow)
# =============================================================================

# WHO-recommended minimum cooling period between whole-blood donations (days)
# Note: Verify against current Drugs and Cosmetics Act, India Schedule C
# ARCHITECTURE.md Remaining Recommendation (Medium priority)
DONATION_COOLING_PERIOD_DAYS: int = 56  # 8 weeks

# =============================================================================
# Emergency Constants
# Architecture Reference: ARCHITECTURE.md Section 30 (Emergency Workflow)
# =============================================================================

# Valid emergency urgency levels
URGENCY_LEVELS: frozenset[str] = frozenset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})

# Initial search radius for donor matching (km)
EMERGENCY_INITIAL_RADIUS_KM: float = 10.0

# Second search radius (escalation level 1)
EMERGENCY_ESCALATION_RADIUS_1_KM: float = 25.0

# Third search radius (escalation level 2)
EMERGENCY_ESCALATION_RADIUS_2_KM: float = 50.0

# Auto-escalation timeouts per urgency level (minutes without donor response)
ESCALATION_TIMEOUT_MINUTES: dict[str, int] = {
    "CRITICAL": 5,
    "HIGH": 10,
    "MEDIUM": 30,
    "LOW": 0,  # No auto-escalation for LOW
}

# Blood inventory reservation timeout (minutes)
# Architecture Reference: ARCHITECTURE.md ADR-001 (Inventory Concurrency)
INVENTORY_RESERVATION_TIMEOUT_MINUTES: int = 30

# =============================================================================
# AI Matching Constants
# Architecture Reference: ARCHITECTURE.md ADR-004 (AI Matching Engine Strategy)
# Scoring weights are configurable parameters — not hardcoded in algorithm
# =============================================================================

# Maximum number of donors returned per match
MAX_DONORS_PER_MATCH: int = 10

# Maximum number of blood banks returned per match
MAX_BLOOD_BANKS_PER_MATCH: int = 5

# Approved scoring weights (ADR-004 — tunable after pilot deployment)
MATCH_WEIGHT_COMPATIBILITY: float = 0.40
MATCH_WEIGHT_PROXIMITY: float = 0.30
MATCH_WEIGHT_AVAILABILITY: float = 0.20
MATCH_WEIGHT_DONATION_HISTORY: float = 0.10

# Compatibility score values
COMPATIBILITY_EXACT_MATCH: float = 1.0
COMPATIBILITY_UNIVERSAL_DONOR: float = 0.8  # e.g., O- donor for non-O- recipient
COMPATIBILITY_INCOMPATIBLE: float = 0.0     # Hard exclusion — never proposed

# Default donation history score for new donors with no history
DONATION_HISTORY_DEFAULT_SCORE: float = 0.0

# =============================================================================
# Caching TTL Constants
# Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
# =============================================================================

CACHE_TTL_INVENTORY_SECONDS: int = 120        # 2 minutes — critical medical data
CACHE_TTL_ANALYTICS_SECONDS: int = 300        # 5 minutes
CACHE_TTL_DONOR_SEARCH_SECONDS: int = 30      # 30 seconds
CACHE_TTL_GEOCODE_SECONDS: int = 86400        # 24 hours
CACHE_TTL_REFRESH_TOKEN_SECONDS: int = 604800  # 7 days

# Redis key prefix (version prefix for easy bulk invalidation)
CACHE_KEY_VERSION: str = "v1"

# =============================================================================
# Pagination Defaults
# =============================================================================

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# =============================================================================
# Donor Availability States
# Architecture Reference: ARCHITECTURE.md Section 33 (Donor Lifecycle)
# =============================================================================

DONOR_STATUS_AVAILABLE: str = "AVAILABLE"
DONOR_STATUS_UNAVAILABLE: str = "UNAVAILABLE"
DONOR_STATUS_COOLING_PERIOD: str = "COOLING_PERIOD"

VALID_DONOR_STATUSES: frozenset[str] = frozenset({
    DONOR_STATUS_AVAILABLE,
    DONOR_STATUS_UNAVAILABLE,
    DONOR_STATUS_COOLING_PERIOD,
})

# =============================================================================
# User Roles
# Architecture Reference: ARCHITECTURE.md FR-01 (9 distinct roles)
# =============================================================================

ROLE_SUPER_ADMIN: str = "SUPER_ADMIN"
ROLE_ADMIN: str = "ADMIN"
ROLE_HOSPITAL_ADMIN: str = "HOSPITAL_ADMIN"
ROLE_HOSPITAL_STAFF: str = "HOSPITAL_STAFF"
ROLE_BLOOD_BANK_MANAGER: str = "BLOOD_BANK_MANAGER"
ROLE_BLOOD_BANK_STAFF: str = "BLOOD_BANK_STAFF"
ROLE_DONOR: str = "DONOR"
ROLE_PATIENT: str = "PATIENT"
ROLE_GOVERNMENT_ANALYST: str = "GOVERNMENT_ANALYST"

ALL_ROLES: frozenset[str] = frozenset({
    ROLE_SUPER_ADMIN,
    ROLE_ADMIN,
    ROLE_HOSPITAL_ADMIN,
    ROLE_HOSPITAL_STAFF,
    ROLE_BLOOD_BANK_MANAGER,
    ROLE_BLOOD_BANK_STAFF,
    ROLE_DONOR,
    ROLE_PATIENT,
    ROLE_GOVERNMENT_ANALYST,
})

# =============================================================================
# Location Constants
# Architecture Reference: ARCHITECTURE.md ADR-002 (Donor Location Privacy Strategy)
# =============================================================================

# Temporary precise GPS TTL in Redis (seconds)
# Architecture: precise GPS never stored in DB; only in Redis with TTL
PRECISE_GPS_REDIS_TTL_SECONDS: int = 1800  # 30 minutes maximum

# Earth radius for Haversine calculation (km)
EARTH_RADIUS_KM: float = 6371.0
