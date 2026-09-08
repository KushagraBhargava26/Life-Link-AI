"""Matching module domain exceptions."""

from app.core.exceptions import LifeLinkException, NotFoundError, ValidationError, ConflictError


class MatchingError(LifeLinkException):
    """Base exception for matching operations."""
    def __init__(self, message: str = "Matching operation failed"):
        super().__init__(message=message, code="MATCHING_ERROR", status_code=500)


class MatchRunNotFoundError(NotFoundError):
    """Raised when a match run is not found."""
    def __init__(self, message: str = "Match run not found"):
        super().__init__(message=message)


class CandidateNotFoundError(NotFoundError):
    """Raised when a match candidate is not found."""
    def __init__(self, message: str = "Match candidate not found"):
        super().__init__(message=message)


class RequestNotEligibleForMatchingError(ValidationError):
    """Raised when an emergency request cannot be matched."""
    def __init__(self, message: str = "Emergency request is not eligible for matching"):
        super().__init__(message=message)
