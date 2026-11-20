"""Standard domain exception hierarchy and error models for Q-TRACE."""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.app.core.logging import get_logger

logger = get_logger("exceptions")


class QTraceException(Exception):
    """Base exception class for all domain-specific errors in Q-TRACE."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundException(QTraceException):
    """Raised when an entity (Case, Evidence, Analysis, etc.) cannot be found."""

    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
            details={"entity_name": entity_name, "entity_id": str(entity_id)},
        )


class IntegrityException(QTraceException):
    """Raised when an integrity check fails or a conflict occurs (e.g. SHA-256 mismatch)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="INTEGRITY_VIOLATION",
            details=details,
        )


class ValidationException(QTraceException):
    """Raised when request payload, file format, magic bytes, or dimensions fail validation."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            error_code="VALIDATION_ERROR",
            details=details,
        )


class StorageException(QTraceException):
    """Raised when an evidence storage or file operation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="STORAGE_ERROR",
            details=details,
        )


class SecurityException(QTraceException):
    """Raised on security violations such as path traversal or forbidden access."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="SECURITY_VIOLATION",
            details=details,
        )


class QuantumProcessingException(QTraceException):
    """Raised when quantum circuit construction, state preparation, or simulation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="QUANTUM_PROCESSING_ERROR",
            details=details,
        )


async def qtrace_exception_handler(request: Request, exc: QTraceException) -> JSONResponse:
    """Handle custom QTraceException and return a structured JSON response."""
    logger.warning(
        f"Domain exception on {request.method} {request.url.path}: "
        f"[{exc.error_code}] {exc.message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught internal exceptions securely without exposing internal stack traces."""
    logger.exception(f"Unhandled error processing {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please contact the administrator.",
                "details": {},
            }
        },
    )

