"""Configuration specific exceptions."""
from __future__ import annotations


class ConfigError(RuntimeError):
    """Raised when configuration loading or validation fails."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause
