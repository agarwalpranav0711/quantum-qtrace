"""API routes for classical digital image forensics engine."""

from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.core.exceptions import EntityNotFoundException, StorageException
from backend.app.storage.service import get_storage_service, StorageService
from backend.app.forensics.registry import get_forensic_registry, ForensicRegistry
from backend.app.forensics.pipeline import ForensicPipeline
from backend.app.forensics.schemas import (
    TechniqueDescriptor,
    AnalysisExecutionRequest,
    AnalysisSummaryResponse,
)
from backend.app.models.artifact import Artifact

router = APIRouter(tags=["Classical Forensics"])


def get_pipeline(db: Session = Depends(get_db)) -> ForensicPipeline:
    """Dependency provider for ForensicPipeline."""
    return ForensicPipeline(db)


def get_registry() -> ForensicRegistry:
    """Dependency provider for ForensicRegistry."""
    return get_forensic_registry()


def get_storage() -> StorageService:
    """Dependency provider for StorageService."""
    return get_storage_service()


@router.get("/forensics/techniques", response_model=List[TechniqueDescriptor])
def list_forensic_techniques(
    registry: ForensicRegistry = Depends(get_registry),
) -> List[TechniqueDescriptor]:
    """Enumerate all registered classical forensic techniques and capabilities."""
    return registry.list_techniques()


@router.post(
    "/evidence/{evidence_id}/analyze",
    response_model=AnalysisSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def run_forensic_analysis(
    evidence_id: str,
    payload: AnalysisExecutionRequest,
    pipeline: ForensicPipeline = Depends(get_pipeline),
) -> AnalysisSummaryResponse:
    """
    Execute configured classical forensic analysis suite on target evidence image.

    Runs requested (or all applicable) algorithms:
    - Error Level Analysis (ELA)
    - Sensor Noise Inconsistency
    - Copy-Move Forgery Detection (CMFD)
    - Image Metadata & EXIF Integrity
    - Multi-Channel Histograms & Statistics
    - Perceptual Hashing (aHash/dHash/pHash)
    - Edge Gradient Discontinuity & Inpainting
    - Multi-Signal Consensus Fusion
    """
    return pipeline.run_analysis(evidence_id, payload)


@router.get(
    "/evidence/{evidence_id}/analyses",
    response_model=List[Dict[str, Any]],
)
def list_evidence_analyses(
    evidence_id: str,
    pipeline: ForensicPipeline = Depends(get_pipeline),
) -> List[Dict[str, Any]]:
    """List historical analysis runs associated with an evidence item."""
    return pipeline.list_analyses_for_evidence(evidence_id)


@router.get(
    "/analysis/{analysis_id}",
    response_model=AnalysisSummaryResponse,
)
def get_analysis_details(
    analysis_id: str,
    pipeline: ForensicPipeline = Depends(get_pipeline),
) -> AnalysisSummaryResponse:
    """Retrieve complete findings, metrics, and artifact references for an analysis run."""
    return pipeline.get_analysis_by_id(analysis_id)


@router.get("/analysis/{analysis_id}/artifacts/{artifact_id}/file")
def get_artifact_file(
    analysis_id: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage),
):
    """
    Stream a generated forensic analysis artifact (heatmaps, difference plots, match lines)
    with strict path isolation and cache validation.
    """
    artifact = (
        db.query(Artifact)
        .filter(Artifact.id == artifact_id, Artifact.analysis_id == analysis_id)
        .one_or_none()
    )
    if not artifact:
        raise EntityNotFoundException("Artifact", artifact_id)

    try:
        resolved_path = storage.retrieve_file("analysis", artifact.stored_filename)
    except StorageException:
        raise EntityNotFoundException("ArtifactFile", artifact.stored_filename)

    return FileResponse(
        path=str(resolved_path),
        media_type="image/png",
        filename=artifact.stored_filename,
        headers={"Cache-Control": "public, max-age=3600"},
    )

