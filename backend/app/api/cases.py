"""API routes for case management, evidence ingestion, and integrity verification."""

from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.case_service import CaseService
from backend.app.core.exceptions import StorageException
from backend.app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseDetailResponse,
    ExaminerNoteCreate,
    ExaminerNoteResponse,
)
from backend.app.schemas.evidence import (
    EvidenceResponse,
    EvidenceVerifyResponse,
)
from backend.app.schemas.common import PaginatedResponse

router = APIRouter(tags=["Cases & Evidence"])


def get_case_service(db: Session = Depends(get_db)) -> CaseService:
    """Dependency provider for CaseService."""
    return CaseService(db)


# --- Case Endpoints ---

@router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreate,
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    """Register a new investigation case."""
    return service.create_case(payload)


@router.get("/cases", response_model=PaginatedResponse[CaseResponse])
def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CaseService = Depends(get_case_service),
) -> PaginatedResponse[CaseResponse]:
    """Retrieve paginated list of cases."""
    skip = (page - 1) * page_size
    items, total = service.list_cases(skip=skip, limit=page_size)
    has_next = (skip + len(items)) < total
    return PaginatedResponse(
        items=[CaseResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
def get_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
) -> CaseDetailResponse:
    """Get detailed case information including evidence count and examiner notes."""
    case = service.get_case_by_id(case_id)
    notes = [ExaminerNoteResponse.model_validate(n) for n in case.notes]
    return CaseDetailResponse(
        id=case.id,
        case_number=case.case_number,
        title=case.title,
        description=case.description,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at,
        evidence_count=len(case.evidence_items),
        notes=notes,
    )


@router.patch("/cases/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: str,
    payload: CaseUpdate,
    service: CaseService = Depends(get_case_service),
) -> CaseResponse:
    """Update case status, title, or description."""
    return service.update_case(case_id, payload)


@router.post("/cases/{case_id}/notes", response_model=ExaminerNoteResponse, status_code=status.HTTP_201_CREATED)
def add_case_note(
    case_id: str,
    payload: ExaminerNoteCreate,
    service: CaseService = Depends(get_case_service),
) -> ExaminerNoteResponse:
    """Attach an examiner note or observation to a case."""
    return service.add_note(case_id, payload)


# --- Evidence Endpoints ---

@router.post("/cases/{case_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_case_evidence(
    case_id: str,
    file: UploadFile = File(..., description="Image evidence file (JPEG, PNG, TIFF)"),
    service: CaseService = Depends(get_case_service),
) -> EvidenceResponse:
    """
    Upload and securely ingest an evidence image for a specific case.

    Enforces WORM storage, magic-byte inspection, decompression bomb guard, and SHA-256 calculation.
    """
    file_bytes = await file.read()
    evidence = service.ingest_evidence(
        case_id=case_id,
        file_bytes=file_bytes,
        original_filename=file.filename or "evidence.bin",
    )
    return EvidenceResponse.model_validate(evidence)


@router.post("/evidence/upload", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence_direct(
    file: UploadFile = File(..., description="Image evidence file (JPEG, PNG, TIFF)"),
    case_id: Optional[str] = Form(None, description="Optional case UUID"),
    service: CaseService = Depends(get_case_service),
) -> EvidenceResponse:
    """
    Direct evidence upload endpoint supporting both unattached and case-associated evidence.
    """
    file_bytes = await file.read()
    evidence = service.ingest_evidence(
        case_id=case_id,
        file_bytes=file_bytes,
        original_filename=file.filename or "evidence.bin",
    )
    return EvidenceResponse.model_validate(evidence)


@router.get("/cases/{case_id}/evidence", response_model=List[EvidenceResponse])
def list_case_evidence(
    case_id: str,
    service: CaseService = Depends(get_case_service),
) -> List[EvidenceResponse]:
    """List all evidence items associated with a case."""
    items = service.list_evidence_for_case(case_id)
    return [EvidenceResponse.model_validate(item) for item in items]


@router.get("/evidence", response_model=PaginatedResponse[EvidenceResponse])
def list_all_evidence(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CaseService = Depends(get_case_service),
) -> PaginatedResponse[EvidenceResponse]:
    """Retrieve paginated list of all evidence across investigations."""
    skip = (page - 1) * page_size
    items, total = service.list_all_evidence(skip=skip, limit=page_size)
    has_next = (skip + len(items)) < total
    return PaginatedResponse(
        items=[EvidenceResponse.model_validate(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(
    evidence_id: str,
    service: CaseService = Depends(get_case_service),
) -> EvidenceResponse:
    """Retrieve evidence metadata by ID."""
    evidence = service.get_evidence_by_id(evidence_id)
    return EvidenceResponse.model_validate(evidence)


@router.get("/evidence/{evidence_id}/file")
def get_evidence_file(
    evidence_id: str,
    service: CaseService = Depends(get_case_service),
):
    """Serve raw evidence image binary stream for forensic preview."""
    evidence = service.get_evidence_by_id(evidence_id)
    path = Path(evidence.storage_path)
    if not path.exists():
        raise StorageException(f"Stored evidence file not found on disk at: {evidence.storage_path}")
    return FileResponse(
        path=path,
        media_type=evidence.mime_type,
        filename=evidence.original_filename,
    )


@router.post("/evidence/{evidence_id}/verify", response_model=EvidenceVerifyResponse)
def verify_evidence_integrity(
    evidence_id: str,
    service: CaseService = Depends(get_case_service),
) -> EvidenceVerifyResponse:
    """
    Perform on-demand cryptographic integrity audit on stored evidence file.
    Re-hashes the physical file on disk and compares it to the original SHA-256 digest.
    """
    return service.audit_evidence_integrity(evidence_id)

