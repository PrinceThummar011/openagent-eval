"""Base exception class for OpenAgent Eval."""

from __future__ import annotations


class OpenAgentEvalError(Exception):
    """Base exception for all OpenAgent Eval errors.

    All custom exceptions in the framework should inherit from this class.
    This enables consistent error handling and catching.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error context.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message

    def __repr__(self) -> str:
        """Return developer-friendly representation."""
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"
