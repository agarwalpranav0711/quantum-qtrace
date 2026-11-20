"""Pydantic schemas for Regions of Interest (ROI), annotations, and image comparison."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ROICreate(BaseModel):
    """Payload to create an examiner or algorithm Region of Interest."""
    roi_label: str = Field(..., max_length=128, description="Human-readable label for region")
    roi_type: str = Field(default="EXAMINER_CREATED", description="EXAMINER_CREATED, ALGORITHM_CANDIDATE, COMPARISON_DELTA")
    x: int = Field(..., ge=0, description="Top-left X in original image pixels")
    y: int = Field(..., ge=0, description="Top-left Y in original image pixels")
    width: int = Field(..., gt=0, description="Region width in original image pixels")
    height: int = Field(..., gt=0, description="Region height in original image pixels")
    color: str = Field(default="#00F2FE", description="Hex color token for UI rendering")
    observation: Optional[str] = Field(None, description="Factual measured property")
    hypothesis: Optional[str] = Field(None, description="Examiner investigative hypothesis")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Examiner-assigned qualitative confidence")
    analysis_id: Optional[str] = Field(None, description="Optional foreign key link to Analysis record")


class ROIUpdate(BaseModel):
    """Payload to update an existing Region of Interest."""
    roi_label: Optional[str] = Field(None, max_length=128)
    x: Optional[int] = Field(None, ge=0)
    y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, gt=0)
    height: Optional[int] = Field(None, gt=0)
    color: Optional[str] = None
    observation: Optional[str] = None
    hypothesis: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class ROIResponse(BaseModel):
    """Public representation of a Region of Interest."""
    id: str
    evidence_id: str
    analysis_id: Optional[str] = None
    roi_label: str
    roi_type: str
    x: int
    y: int
    width: int
    height: int
    color: str
    observation: Optional[str] = None
    hypothesis: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ROICropResponse(BaseModel):
    """Metadata describing a generated cropped derivative artifact."""
    roi_id: str
    evidence_id: str
    artifact_id: str
    stored_filename: str
    sha256_hash: str
    crop_x: int
    crop_y: int
    crop_width: int
    crop_height: int
    suggested_quantum_patch: Optional[List[List[int]]] = None


class ImageComparisonRequest(BaseModel):
    """Payload to execute visual difference and alignment comparison between two images."""
    primary_evidence_id: str = Field(..., description="Original/Reference evidence UUID")
    comparison_evidence_id: str = Field(..., description="Second evidence UUID to compare")
    align_images: bool = Field(default=True, description="Attempt automated feature-based homography alignment")
    difference_threshold: int = Field(default=15, ge=0, le=255, description="Sensitivity threshold for diff counting")
    manual_offset_x: int = Field(default=0, description="Manual X offset applied to comparison image")
    manual_offset_y: int = Field(default=0, description="Manual Y offset applied to comparison image")


class ImageComparisonResponse(BaseModel):
    """Comprehensive comparison metrics, alignment details, and difference artifact references."""
    primary_evidence_id: str
    comparison_evidence_id: str
    identical_dimensions: bool
    primary_dimensions: Dict[str, int]
    comparison_dimensions: Dict[str, int]
    alignment_performed: bool
    alignment_method: str
    alignment_status: str
    transformation_matrix: Optional[List[List[float]]] = None
    difference_pixel_count: int
    difference_percentage: float
    mean_absolute_error: float
    root_mean_square_error: float
    psnr_db: float
    ssim_score: float
    artifact_id: Optional[str] = None
    artifact_filename: Optional[str] = None
    suggested_quantum_patch_a: Optional[List[List[int]]] = None
    suggested_quantum_patch_b: Optional[List[List[int]]] = None
    warnings: List[str] = Field(default_factory=list)

