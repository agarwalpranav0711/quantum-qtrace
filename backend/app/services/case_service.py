"""Case and evidence management business logic."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.app.models.case import Case
from backend.app.models.evidence import Evidence
from backend.app.models.note import ExaminerNote
from backend.app.schemas.case import CaseCreate, CaseUpdate, ExaminerNoteCreate
from backend.app.schemas.evidence import EvidenceVerifyResponse
from backend.app.core.exceptions import EntityNotFoundException, IntegrityException
from backend.app.services.validation import validate_image_file
from backend.app.services.integrity import compute_sha256_bytes, verify_file_integrity
from backend.app.storage.service import get_storage_service
from backend.app.core.logging import get_logger

logger = get_logger("case_service")


class CaseService:
    """Coordinates forensic case workflows, evidence ingestion, and integrity auditing."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = get_storage_service()

    def create_case(self, payload: CaseCreate) -> Case:
        """Register a new investigation case."""
        existing = self.db.execute(
            select(Case).where(Case.case_number == payload.case_number)
        ).scalar_one_or_none()

        if existing:
            raise IntegrityException(
                f"A case with case number '{payload.case_number}' already exists."
            )

        new_case = Case(
            case_number=payload.case_number,
            title=payload.title,
            description=payload.description,
            status="OPEN",
        )
        self.db.add(new_case)
        self.db.commit()
        self.db.refresh(new_case)
        logger.info(f"Created forensic case: {new_case.case_number} (ID: {new_case.id})")
        return new_case

    def get_case_by_id(self, case_id: str) -> Case:
        """Fetch a case by its internal UUID identifier."""
        case = self.db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
        if not case:
            raise EntityNotFoundException("Case", case_id)
        return case

    def get_case_by_number(self, case_number: str) -> Case:
        """Fetch a case by its public case number."""
        case = self.db.execute(
            select(Case).where(Case.case_number == case_number)
        ).scalar_one_or_none()
        if not case:
            raise EntityNotFoundException("Case", case_number)
        return case

    def list_cases(self, skip: int = 0, limit: int = 50) -> Tuple[List[Case], int]:
        """List cases with pagination support."""
        total = self.db.execute(select(func.count(Case.id))).scalar_one()
        cases = self.db.execute(
            select(Case).order_by(Case.created_at.desc()).offset(skip).limit(limit)
        ).scalars().all()
        return list(cases), total

    def update_case(self, case_id: str, payload: CaseUpdate) -> Case:
        """Update case metadata or status."""
        case = self.get_case_by_id(case_id)
        if payload.title is not None:
            case.title = payload.title
        if payload.description is not None:
            case.description = payload.description
        if payload.status is not None:
            case.status = payload.status

        self.db.commit()
        self.db.refresh(case)
        return case

    def add_note(self, case_id: str, payload: ExaminerNoteCreate) -> ExaminerNote:
        """Add an examiner note to a case."""
        case = self.get_case_by_id(case_id)

        if payload.evidence_id:
            evidence = self.db.execute(
                select(Evidence).where(Evidence.id == payload.evidence_id)
            ).scalar_one_or_none()
            if not evidence:
                raise EntityNotFoundException("Evidence", payload.evidence_id)

        note = ExaminerNote(
            case_id=case.id,
            evidence_id=payload.evidence_id,
            author=payload.author or "Examiner",
            content=payload.content,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def ingest_evidence(
        self,
        case_id: Optional[str],
        file_bytes: bytes,
        original_filename: str,
    ) -> Evidence:
        """
        Validate, hash, store, and register an evidence image file under WORM guarantees.
        """
        if case_id:
            self.get_case_by_id(case_id)  # Verifies case exists

        # 1. Multi-stage security validation
        validation = validate_image_file(file_bytes, original_filename)

        # 2. Cryptographic SHA-256 hash
        sha256_hash = compute_sha256_bytes(file_bytes)

        # 3. WORM storage preservation
        target_path, stored_filename = self.storage.store_original(
            file_bytes=file_bytes,
            sha256_hash=sha256_hash,
            original_filename=validation.sanitized_filename,
        )

        # 4. Database registration
        evidence = Evidence(
            case_id=case_id,
            original_filename=validation.sanitized_filename,
            stored_filename=stored_filename,
            storage_path=str(target_path),
            mime_type=validation.mime_type,
            file_size=validation.file_size,
            sha256_hash=sha256_hash,
            width=validation.width,
            height=validation.height,
            status="VERIFIED",
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)

        logger.info(
            f"Evidence ingested: '{evidence.original_filename}' -> {stored_filename} "
            f"(SHA256: {sha256_hash[:12]}...)"
        )
        return evidence

    def get_evidence_by_id(self, evidence_id: str) -> Evidence:
        """Retrieve evidence record by ID."""
        evidence = self.db.execute(
            select(Evidence).where(Evidence.id == evidence_id)
        ).scalar_one_or_none()
        if not evidence:
            raise EntityNotFoundException("Evidence", evidence_id)
        return evidence

    def list_evidence_for_case(self, case_id: str) -> List[Evidence]:
        """List all evidence attached to a given case."""
        self.get_case_by_id(case_id)
        items = self.db.execute(
            select(Evidence).where(Evidence.case_id == case_id).order_by(Evidence.created_at.asc())
        ).scalars().all()
        return list(items)

    def list_all_evidence(self, skip: int = 0, limit: int = 50) -> Tuple[List[Evidence], int]:
        """List all evidence across cases with pagination."""
        total = self.db.execute(select(func.count(Evidence.id))).scalar_one()
        items = self.db.execute(
            select(Evidence).order_by(Evidence.created_at.desc()).offset(skip).limit(limit)
        ).scalars().all()
        return list(items), total

    def audit_evidence_integrity(self, evidence_id: str) -> EvidenceVerifyResponse:
        """
        Perform on-demand cryptographic verification of stored evidence on disk.
        """
        evidence = self.get_evidence_by_id(evidence_id)
        is_intact, current_hash = verify_file_integrity(
            evidence.storage_path, evidence.sha256_hash
        )

        new_status = "VERIFIED" if is_intact else "COMPROMISED"
        if evidence.status != new_status:
            evidence.status = new_status
            self.db.commit()

        message = (
            "Evidence file bitstream is identical to original ingestion hash."
            if is_intact
            else "WARNING: Stored evidence hash does not match original ingestion hash! Bitstream tampering detected."
        )

        from datetime import datetime, timezone
        return EvidenceVerifyResponse(
            evidence_id=evidence.id,
            original_filename=evidence.original_filename,
            stored_sha256=evidence.sha256_hash,
            current_sha256=current_hash,
            is_intact=is_intact,
            verified_at=datetime.now(timezone.utc),
            status=new_status,
            message=message,
        )

