"""Custom exceptions for the Duolingo tracker."""
from __future__ import annotations


class DuolingoTrackerError(Exception):
    """Base exception for Duolingo tracker."""
    pass


class ScrapingError(DuolingoTrackerError):
    """Raised when scraping fails."""
    pass


class ConfigError(DuolingoTrackerError):
    """Raised when configuration is invalid."""
    pass


class DataError(DuolingoTrackerError):
    """Raised when data processing fails."""
    pass


class NotificationError(DuolingoTrackerError):
    """Raised when notification sending fails."""
    pass 