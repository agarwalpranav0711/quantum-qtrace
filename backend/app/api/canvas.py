"""API routes for Forensic Canvas: ROI management, derived crops, and image comparison."""

from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.core.exceptions import EntityNotFoundException, StorageException
from backend.app.storage.service import get_storage_service, StorageService
from backend.app.services.canvas_service import CanvasService
from backend.app.schemas.roi import (
    ROICreate,
    ROIUpdate,
    ROIResponse,
    ROICropResponse,
    ImageComparisonRequest,
    ImageComparisonResponse,
)
from backend.app.models.artifact import Artifact

router = APIRouter(tags=["Forensic Canvas & Comparison"])


def get_canvas_service(db: Session = Depends(get_db)) -> CanvasService:
    """Dependency provider for CanvasService."""
    return CanvasService(db)


def get_storage() -> StorageService:
    """Dependency provider for StorageService."""
    return get_storage_service()


# --- ROI Endpoints ---

@router.post(
    "/evidence/{evidence_id}/rois",
    response_model=ROIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_roi(
    evidence_id: str,
    payload: ROICreate,
    service: CanvasService = Depends(get_canvas_service),
) -> ROIResponse:
    """Register a new Region of Interest (ROI) with boundary coordinates and annotations."""
    roi = service.create_roi(evidence_id, payload)
    return ROIResponse.model_validate(roi)


@router.get(
    "/evidence/{evidence_id}/rois",
    response_model=List[ROIResponse],
)
def list_evidence_rois(
    evidence_id: str,
    service: CanvasService = Depends(get_canvas_service),
) -> List[ROIResponse]:
    """List all Regions of Interest associated with an evidence item."""
    rois = service.list_rois_for_evidence(evidence_id)
    return [ROIResponse.model_validate(r) for r in rois]


@router.get(
    "/rois/{roi_id}",
    response_model=ROIResponse,
)
def get_roi_details(
    roi_id: str,
    service: CanvasService = Depends(get_canvas_service),
) -> ROIResponse:
    """Retrieve full details of an individual Region of Interest."""
    roi = service.get_roi_by_id(roi_id)
    return ROIResponse.model_validate(roi)


@router.patch(
    "/rois/{roi_id}",
    response_model=ROIResponse,
)
def update_roi(
    roi_id: str,
    payload: ROIUpdate,
    service: CanvasService = Depends(get_canvas_service),
) -> ROIResponse:
    """Update ROI coordinates, label, color, or examiner observations/hypotheses."""
    roi = service.update_roi(roi_id, payload)
    return ROIResponse.model_validate(roi)


@router.delete(
    "/rois/{roi_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_roi(
    roi_id: str,
    service: CanvasService = Depends(get_canvas_service),
):
    """Delete a Region of Interest."""
    service.delete_roi(roi_id)
    return None


@router.post(
    "/rois/{roi_id}/crop",
    response_model=ROICropResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_roi_crop_artifact(
    roi_id: str,
    service: CanvasService = Depends(get_canvas_service),
) -> ROICropResponse:
    """
    Extract the specified ROI as a discrete derivative crop artifact.
    Preserves original evidence, calculates SHA-256 hash, and generates 4x4 quantum patch.
    """
    return service.generate_roi_crop(roi_id)


# --- Image Comparison Endpoints ---

@router.post(
    "/evidence/compare",
    response_model=ImageComparisonResponse,
    status_code=status.HTTP_200_OK,
)
def compare_evidence_images(
    payload: ImageComparisonRequest,
    service: CanvasService = Depends(get_canvas_service),
) -> ImageComparisonResponse:
    """
    Execute visual difference, feature-based alignment, and statistical error comparison between two images.
    Returns MAE, RMSE, PSNR, SSIM, and dual 4x4 quantum matrices.
    """
    return service.compare_images(payload)


# --- Derivative Artifact Streaming ---

@router.get("/derivatives/{artifact_id}/file")
def stream_derivative_artifact(
    artifact_id: str,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage),
):
    """Stream a generated derivative crop or comparison difference artifact binary file with strict path isolation."""
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).one_or_none()
    if not artifact:
        raise EntityNotFoundException("Artifact", artifact_id)

    resolved_path = None
    for cat in ["derivatives", "analysis"]:
        try:
            resolved_path = storage.retrieve_file(cat, artifact.stored_filename)
            break
        except StorageException:
            continue

    if not resolved_path and artifact.file_path:
        p = Path(artifact.file_path).resolve()
        if p.exists() and str(p).startswith(str(storage.root)):
            resolved_path = p

    if not resolved_path:
        raise EntityNotFoundException("ArtifactFile", artifact.stored_filename)

    return FileResponse(
        path=str(resolved_path),
        media_type="image/png",
        filename=artifact.stored_filename,
        headers={"Cache-Control": "public, max-age=3600"},
    )

