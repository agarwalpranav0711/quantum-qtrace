"""Evidence schemas for uploads, metadata, and integrity verification."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EvidenceResponse(BaseModel):
    """View schema for an ingested evidence item."""
    id: str
    case_id: Optional[str]
    original_filename: str
    stored_filename: str
    storage_path: str
    mime_type: str
    file_size: int
    sha256_hash: str
    width: Optional[int]
    height: Optional[int]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceVerifyResponse(BaseModel):
    """Cryptographic integrity verification result."""
    evidence_id: str
    original_filename: str
    stored_sha256: str
    current_sha256: str
    is_intact: bool
    verified_at: datetime
    status: str
    message: str

