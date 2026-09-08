# backend/app/core/medical.py
# LifeLink AI — Canonical Blood Compatibility and Medical Domain Rules
# Architecture Reference: ARCHITECTURE.md Section 17, 24, ADR-003
#
# Pure Python standard library implementation with ZERO machine learning or external dependencies.
# Deterministic application-level compatibility matrix for Whole Blood, RBC, and Plasma.

from __future__ import annotations

from typing import FrozenSet

VALID_BLOOD_TYPES: FrozenSet[str] = frozenset({
    "O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"
})

VALID_ABO_GROUPS: FrozenSet[str] = frozenset({"O", "A", "B", "AB"})

VALID_COMPONENTS: FrozenSet[str] = frozenset({
    "WHOLE_BLOOD", "RBC", "PLASMA", "PLATELETS", "CRYOPRECIPITATE"
})

# ---------------------------------------------------------------------------
# Red Blood Cell / Whole Blood Compatibility Matrix
# Recipient Blood Type -> Set of compatible Donor Blood Types
# ---------------------------------------------------------------------------
RBC_COMPATIBILITY_MAP: dict[str, frozenset[str]] = {
    "O-": frozenset({"O-"}),
    "O+": frozenset({"O-", "O+"}),
    "A-": frozenset({"O-", "A-"}),
    "A+": frozenset({"O-", "O+", "A-", "A+"}),
    "B-": frozenset({"O-", "B-"}),
    "B+": frozenset({"O-", "O+", "B-", "B+"}),
    "AB-": frozenset({"O-", "A-", "B-", "AB-"}),
    "AB+": frozenset({"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}),
}

# ---------------------------------------------------------------------------
# Plasma (FFP) Compatibility Matrix
# Plasma contains antibodies, so compatibility is inverted compared to RBCs.
# Recipient Blood Type -> Set of compatible Plasma Donor Blood Types
# ---------------------------------------------------------------------------
PLASMA_COMPATIBILITY_MAP: dict[str, frozenset[str]] = {
    "O-": frozenset({"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}),
    "O+": frozenset({"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}),
    "A-": frozenset({"A-", "A+", "AB-", "AB+"}),
    "A+": frozenset({"A-", "A+", "AB-", "AB+"}),
    "B-": frozenset({"B-", "B+", "AB-", "AB+"}),
    "B+": frozenset({"B-", "B+", "AB-", "AB+"}),
    "AB-": frozenset({"AB-", "AB+"}),
    "AB+": frozenset({"AB-", "AB+"}),
}


def parse_blood_type(blood_type: str) -> tuple[str, bool]:
    """
    Parse a unified blood type string (e.g. 'A+', 'O-') into (abo_group, is_rh_positive).
    Raises ValueError on invalid blood type.
    """
    cleaned = blood_type.strip().upper()
    if cleaned not in VALID_BLOOD_TYPES:
        raise ValueError(f"Invalid blood type '{blood_type}'. Expected one of {sorted(VALID_BLOOD_TYPES)}")

    if cleaned.endswith("+"):
        return cleaned[:-1], True
    elif cleaned.endswith("-"):
        return cleaned[:-1], False
    raise ValueError(f"Invalid Rh indicator in blood type '{blood_type}'")


def format_blood_type(abo_group: str, is_rh_positive: bool) -> str:
    """Format (abo_group, is_rh_positive) into standard unified string (e.g. 'A+')."""
    abo = abo_group.strip().upper()
    if abo not in VALID_ABO_GROUPS:
        raise ValueError(f"Invalid ABO group '{abo_group}'")
    return f"{abo}{'+' if is_rh_positive else '-'}"


def get_compatible_donor_types(
    recipient_blood_type: str,
    component: str = "WHOLE_BLOOD",
) -> frozenset[str]:
    """
    Return the set of donor blood types that can be transfused to a recipient of recipient_blood_type.
    """
    recipient = recipient_blood_type.strip().upper()
    comp = component.strip().upper()

    if recipient not in VALID_BLOOD_TYPES:
        raise ValueError(f"Invalid recipient blood type '{recipient_blood_type}'")

    if comp in ("WHOLE_BLOOD", "RBC", "PLATELETS", "CRYOPRECIPITATE"):
        return RBC_COMPATIBILITY_MAP.get(recipient, frozenset())
    elif comp == "PLASMA":
        return PLASMA_COMPATIBILITY_MAP.get(recipient, frozenset())
    else:
        return RBC_COMPATIBILITY_MAP.get(recipient, frozenset())


def is_compatible(
    donor_blood_type: str,
    recipient_blood_type: str,
    component: str = "WHOLE_BLOOD",
) -> bool:
    """
    Check whether a donor blood type is compatible with a recipient blood type.
    Pure deterministic application check.
    """
    donor = donor_blood_type.strip().upper()
    compatible_types = get_compatible_donor_types(recipient_blood_type, component)
    return donor in compatible_types
