"""FastAPI endpoints for forensic investigation dossiers, preview, sections, and exports."""

from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.exceptions import EntityNotFoundException, ValidationException
from backend.app.database.session import get_db
from backend.app.models.dossier import DossierModel, DossierExportModel
from backend.app.schemas.dossier import (
    DossierCreate,
    DossierUpdate,
    DossierResponse,
    DossierSectionItem,
    DossierSectionUpdate,
    DossierExportResponse,
    DossierPreviewResponse,
)
from backend.app.services.dossier_service import dossier_service

router = APIRouter(tags=["Dossiers & Forensic Reports"])
settings = get_settings()


def _format_dossier_response(dossier: DossierModel, db: Session) -> DossierResponse:
    """Helper to convert DossierModel into rich DossierResponse with export counts."""
    latest_export = (
        db.query(DossierExportModel)
        .filter(DossierExportModel.dossier_id == dossier.id)
        .order_by(DossierExportModel.created_at.desc())
        .first()
    )
    export_count = (
        db.query(DossierExportModel)
        .filter(DossierExportModel.dossier_id == dossier.id)
        .count()
    )

    latest_export_resp = None
    if latest_export:
        latest_export_resp = DossierExportResponse.model_validate(latest_export)

    return DossierResponse(
        id=dossier.id,
        case_id=dossier.case_id,
        dossier_number=dossier.dossier_number,
        title=dossier.title,
        author=dossier.author,
        status=dossier.status,
        version=dossier.version,
        confidentiality_level=dossier.confidentiality_level,
        investigation_scope=dossier.investigation_scope,
        executive_summary=dossier.executive_summary,
        examiner_conclusions=dossier.examiner_conclusions,
        recommendations=dossier.recommendations,
        limitations=dossier.limitations,
        configuration_json=dossier.configuration_json,
        created_at=dossier.created_at,
        updated_at=dossier.updated_at,
        sections=[DossierSectionItem.model_validate(s) for s in dossier.sections],
        latest_export=latest_export_resp,
        export_count=export_count,
    )


@router.post(
    "/cases/{case_id}/dossiers",
    response_model=DossierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case_dossier(
    case_id: str,
    payload: DossierCreate,
    db: Session = Depends(get_db),
) -> DossierResponse:
    """Create a new forensic investigation dossier linked to a case."""
    dossier = dossier_service.create_dossier(db, case_id, payload)
    return _format_dossier_response(dossier, db)


@router.get(
    "/cases/{case_id}/dossiers",
    response_model=List[DossierResponse],
    status_code=status.HTTP_200_OK,
)
def list_case_dossiers(
    case_id: str,
    db: Session = Depends(get_db),
) -> List[DossierResponse]:
    """List all dossiers associated with a case."""
    dossiers = dossier_service.list_case_dossiers(db, case_id)
    return [_format_dossier_response(d, db) for d in dossiers]


@router.get(
    "/dossiers/{dossier_id}",
    response_model=DossierResponse,
    status_code=status.HTTP_200_OK,
)
def get_dossier(
    dossier_id: str,
    db: Session = Depends(get_db),
) -> DossierResponse:
    """Retrieve full details of a specific dossier."""
    dossier = dossier_service.get_dossier(db, dossier_id)
    return _format_dossier_response(dossier, db)


@router.patch(
    "/dossiers/{dossier_id}",
    response_model=DossierResponse,
    status_code=status.HTTP_200_OK,
)
def update_dossier(
    dossier_id: str,
    payload: DossierUpdate,
    db: Session = Depends(get_db),
) -> DossierResponse:
    """Update dossier narrative fields, status, or included evidence/analyses configuration."""
    dossier = dossier_service.update_dossier(db, dossier_id, payload)
    return _format_dossier_response(dossier, db)


@router.delete(
    "/dossiers/{dossier_id}",
    status_code=status.HTTP_200_OK,
)
def delete_dossier(
    dossier_id: str,
    db: Session = Depends(get_db),
):
    """Delete a dossier and its section configurations."""
    success = dossier_service.delete_dossier(db, dossier_id)
    return {"success": success, "dossier_id": dossier_id}


@router.patch(
    "/dossiers/{dossier_id}/sections/{section_id}",
    response_model=DossierSectionItem,
    status_code=status.HTTP_200_OK,
)
def update_dossier_section(
    dossier_id: str,
    section_id: str,
    payload: DossierSectionUpdate,
    db: Session = Depends(get_db),
) -> DossierSectionItem:
    """Update title, ordering, enablement, or custom narrative override of a dossier section."""
    section = dossier_service.update_dossier_section(db, dossier_id, section_id, payload)
    return DossierSectionItem.model_validate(section)


@router.get(
    "/dossiers/{dossier_id}/preview",
    response_model=DossierPreviewResponse,
    status_code=status.HTTP_200_OK,
)
def preview_dossier(
    dossier_id: str,
    db: Session = Depends(get_db),
) -> DossierPreviewResponse:
    """
    Compile and preview the complete structured dossier payload with all
    associated evidence records, verification manifests, telemetry, and ROIs.
    """
    snapshot = dossier_service.compile_dossier_snapshot(db, dossier_id)
    return DossierPreviewResponse.model_validate(snapshot)


@router.post(
    "/dossiers/{dossier_id}/export/pdf",
    response_model=DossierExportResponse,
    status_code=status.HTTP_201_CREATED,
)
def export_dossier_pdf(
    dossier_id: str,
    db: Session = Depends(get_db),
) -> DossierExportResponse:
    """
    Generate and save a multi-page courtroom-grade PDF forensic dossier.
    Computes SHA-256 digest and records frozen snapshot in the export history.
    """
    export = dossier_service.export_dossier_pdf(db, dossier_id)
    return DossierExportResponse.model_validate(export)


@router.post(
    "/dossiers/{dossier_id}/export/json",
    response_model=DossierExportResponse,
    status_code=status.HTTP_201_CREATED,
)
def export_dossier_json(
    dossier_id: str,
    db: Session = Depends(get_db),
) -> DossierExportResponse:
    """
    Generate and save an open, machine-readable JSON forensic dossier.
    Computes SHA-256 digest and records frozen snapshot in the export history.
    """
    export = dossier_service.export_dossier_json(db, dossier_id)
    return DossierExportResponse.model_validate(export)


@router.get(
    "/dossiers/{dossier_id}/exports",
    response_model=List[DossierExportResponse],
    status_code=status.HTTP_200_OK,
)
def list_dossier_exports(
    dossier_id: str,
    db: Session = Depends(get_db),
) -> List[DossierExportResponse]:
    """Retrieve the full historical version ledger of exported PDF and JSON reports."""
    exports = (
        db.query(DossierExportModel)
        .filter(DossierExportModel.dossier_id == dossier_id)
        .order_by(DossierExportModel.created_at.desc())
        .all()
    )
    return [DossierExportResponse.model_validate(e) for e in exports]


@router.get("/dossiers/{dossier_id}/exports/{export_id}/file")
def download_dossier_export_file(
    dossier_id: str,
    export_id: str,
    db: Session = Depends(get_db),
):
    """Download the physical exported PDF or JSON document with strict path safety."""
    export = db.get(DossierExportModel, export_id)
    if not export or export.dossier_id != dossier_id:
        raise EntityNotFoundException(f"Dossier export '{export_id}' not found.")

    storage_root = Path(settings.STORAGE_ROOT).resolve()
    file_path = (storage_root / export.storage_path.replace("storage/", "")).resolve()

    if not file_path.exists():
        raise EntityNotFoundException(f"Physical report file '{export.filename}' not found on disk.")

    media_type = "application/pdf" if export.export_format == "PDF" else "application/json"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=export.filename,
        headers={
            "Content-Disposition": f'attachment; filename="{export.filename}"',
            "X-Report-SHA256": export.sha256_hash,
            "X-Report-Version": str(export.version),
        },
    )

