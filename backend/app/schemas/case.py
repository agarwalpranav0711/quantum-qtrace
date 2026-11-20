"""Case and ExaminerNote schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExaminerNoteCreate(BaseModel):
    """Payload to create an examiner note."""
    content: str = Field(..., min_length=1)
    author: Optional[str] = "Examiner"
    evidence_id: Optional[str] = None


class ExaminerNoteResponse(BaseModel):
    """Examiner note view schema."""
    id: str
    case_id: str
    evidence_id: Optional[str]
    author: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseCreate(BaseModel):
    """Payload to register a new forensic case."""
    case_number: str = Field(..., min_length=3, max_length=64, description="Unique case number e.g. QC-2026-001")
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None


class CaseUpdate(BaseModel):
    """Payload to update an existing case."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, description="OPEN, IN_PROGRESS, CLOSED, ARCHIVED")


class CaseResponse(BaseModel):
    """Standard case view schema."""
    id: str
    case_number: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseDetailResponse(CaseResponse):
    """Detailed case view schema including related evidence count and notes."""
    evidence_count: int = 0
    notes: List[ExaminerNoteResponse] = []

    model_config = ConfigDict(from_attributes=True)

