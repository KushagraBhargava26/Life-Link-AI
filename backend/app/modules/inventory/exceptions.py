# backend/app/modules/inventory/exceptions.py
# LifeLink AI — Blood Inventory Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 37; API.md Section 10

from __future__ import annotations

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError


class InventoryNotFoundError(NotFoundError):
    """Raised when an inventory item is not found."""

    def __init__(self, message: str = "Blood inventory record not found") -> None:
        super().__init__(message=message, code="INVENTORY_NOT_FOUND")


class InsufficientStockError(ValidationError):
    """Raised when available blood units are insufficient for the requested operation."""

    def __init__(self, message: str = "Insufficient blood inventory units available") -> None:
        super().__init__(message=message, code="INVENTORY_INSUFFICIENT_STOCK")


class InventoryPermissionDeniedError(ForbiddenError):
    """Raised when an inventory action is denied due to lack of facility ownership."""

    def __init__(self, message: str = "Permission denied to manage inventory for this facility") -> None:
        super().__init__(message=message, code="INVENTORY_PERMISSION_DENIED")


class InvalidInventoryOperationError(ValidationError):
    """Raised when an invalid operation is performed on blood inventory."""

    def __init__(self, message: str = "Invalid inventory adjustment or operation") -> None:
        super().__init__(message=message, code="INVENTORY_INVALID_OPERATION")
