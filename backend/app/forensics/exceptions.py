"""Domain exceptions for classical image forensics engine."""

from backend.app.core.exceptions import AppBaseException


class ForensicException(AppBaseException):
    """Base exception for forensic analysis failures."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message=message, status_code=status_code)


class UnsupportedImageException(ForensicException):
    """Raised when an image format or dimension cannot be processed by a technique."""
    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=400)


class TechniqueExecutionException(ForensicException):
    """Raised when an individual forensic algorithm fails during execution."""
    def __init__(self, technique_id: str, message: str) -> None:
        super().__init__(message=f"Technique '{technique_id}' execution failed: {message}", status_code=500)

