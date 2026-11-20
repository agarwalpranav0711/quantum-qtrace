"""Common Pydantic schemas for standardized API responses and pagination."""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIErrorDetails(BaseModel):
    """Structured error details."""
    code: str
    message: str
    details: Optional[dict] = None


class APIErrorResponse(BaseModel):
    """Standardized error envelope."""
    error: APIErrorDetails


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic envelope for paginated collections."""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool

    model_config = ConfigDict(from_attributes=True)

