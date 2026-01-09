"""
Custom exceptions for Tarka Cloud Compute Referee.
"""


class TarkaError(Exception):
    """Base exception for all Tarka errors."""
    pass


class InvalidInputError(TarkaError):
    """Raised when input validation fails."""
    pass


class ScoringError(TarkaError):
    """Raised when scoring logic encounters an error."""
    pass


class ConfigurationError(TarkaError):
    """Raised when configuration is invalid."""
    pass
