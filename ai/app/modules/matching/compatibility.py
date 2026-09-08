# ai/app/modules/matching/compatibility.py
# LifeLink AI — ABO/Rh Blood Compatibility Matrix
# Architecture Reference: ARCHITECTURE.md Section 32 (Blood Compatibility Matrix)
# Architecture Reference: ARCHITECTURE.md ADR-003 (Blood Group Data Model)
#
# CRITICAL: This matrix is a medical safety constraint.
# No match is EVER proposed that violates this table.
# Rule: ABO/Rh compatibility is a HARD FILTER applied before any scoring.

from __future__ import annotations

# Blood compatibility matrix
# Maps: donor ABO group → frozenset of compatible recipient ABO groups
# Architecture Reference: ARCHITECTURE.md Section 32
ABO_COMPATIBILITY_MATRIX: dict[str, frozenset[str]] = {
    "O": frozenset({"O", "A", "B", "AB"}),  # O is universal donor
    "A": frozenset({"A", "AB"}),
    "B": frozenset({"B", "AB"}),
    "AB": frozenset({"AB"}),               # AB can only donate to AB
}


def is_abo_compatible(donor_abo: str, recipient_abo: str) -> bool:
    """
    Check ABO blood group compatibility.

    Args:
        donor_abo: Donor's ABO group (A, B, AB, or O).
        recipient_abo: Recipient's ABO group.

    Returns:
        True if donor can donate to recipient, False otherwise.
    """
    compatible_recipients = ABO_COMPATIBILITY_MATRIX.get(donor_abo, frozenset())
    return recipient_abo in compatible_recipients


def is_rh_compatible(donor_rh_positive: bool, recipient_rh_positive: bool) -> bool:
    """
    Check Rh factor compatibility.

    Rules (ARCHITECTURE.md Section 32):
    - Rh-positive recipient can receive Rh+ or Rh- blood.
    - Rh-negative recipient can ONLY receive Rh- blood.

    Args:
        donor_rh_positive: True if donor is Rh positive.
        recipient_rh_positive: True if recipient is Rh positive.

    Returns:
        True if compatible, False otherwise.
    """
    if recipient_rh_positive:
        return True  # Rh+ recipient can receive both
    else:
        return not donor_rh_positive  # Rh- recipient can only receive Rh-


def is_compatible(donor_abo: str, donor_rh_positive: bool, recipient_abo: str, recipient_rh_positive: bool) -> bool:
    """
    Check full blood compatibility (ABO + Rh).

    This is the primary HARD FILTER in the matching engine.
    Architecture Reference: ARCHITECTURE.md ADR-004

    Args:
        donor_abo: Donor ABO group.
        donor_rh_positive: Donor Rh factor.
        recipient_abo: Recipient ABO group.
        recipient_rh_positive: Recipient Rh factor.

    Returns:
        True if donor can donate to this recipient. False is a hard exclusion.
    """
    return (
        is_abo_compatible(donor_abo, recipient_abo)
        and is_rh_compatible(donor_rh_positive, recipient_rh_positive)
    )


def get_compatibility_score(donor_abo: str, donor_rh_positive: bool, recipient_abo: str, recipient_rh_positive: bool) -> float:
    """
    Get the compatibility score for a donor-recipient pair.

    Architecture Reference: ARCHITECTURE.md ADR-004 (Scoring Weights)
    - 1.0: Exact ABO + Rh match
    - 0.8: Universal donor type (e.g., O- giving to non-O-)
    - 0.0: Incompatible (hard exclusion)

    Args:
        donor_abo, donor_rh_positive: Donor blood type.
        recipient_abo, recipient_rh_positive: Recipient blood type.

    Returns:
        Score between 0.0 and 1.0.
    """
    if not is_compatible(donor_abo, donor_rh_positive, recipient_abo, recipient_rh_positive):
        return 0.0  # Hard exclusion

    if donor_abo == recipient_abo and donor_rh_positive == recipient_rh_positive:
        return 1.0  # Exact match

    # Universal donor cases (e.g., O- donating to A+, B+, etc.)
    return 0.8
