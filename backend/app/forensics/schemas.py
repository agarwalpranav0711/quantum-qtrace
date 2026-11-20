"""Pydantic schemas and data models for classical image forensics engine."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ForensicStatus(str, Enum):
    """Normalized forensic technique outcome status."""
    NO_ANOMALY_DETECTED = "NO_ANOMALY_DETECTED"
    POTENTIAL_INDICATOR_DETECTED = "POTENTIAL_INDICATOR_DETECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"


class FindingCategory(str, Enum):
    """Taxonomic level for evidence findings."""
    OBSERVATION = "OBSERVATION"       # Directly measured, factual technical property
    INDICATOR = "INDICATOR"           # Statistical or signal anomaly warranting review
    HYPOTHESIS = "HYPOTHESIS"         # Potential explanation requiring investigation
    CONCLUSION = "CONCLUSION"         # Examiner human-reviewed verdict


class FindingItem(BaseModel):
    """Individual observation, indicator, or hypothesis produced by analysis."""
    category: FindingCategory
    title: str = Field(..., description="Short descriptive title of the finding")
    description: str = Field(..., description="Technical detail and context of the measurement")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in measurement (not fraud probability)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Numerical details, coordinates, or measurements")


class RegionOfInterest(BaseModel):
    """Bounding box and metrics for a candidate anomalous region."""
    roi_id: str
    x: int = Field(..., description="Top-left X coordinate")
    y: int = Field(..., description="Top-left Y coordinate")
    width: int = Field(..., description="Region width in pixels")
    height: int = Field(..., description="Region height in pixels")
    score: float = Field(..., ge=0.0, le=1.0, description="Local anomaly / consensus score")
    contributing_techniques: List[str] = Field(default_factory=list)
    suggested_quantum_patch: Optional[List[List[int]]] = Field(
        None, description="Quantized 4x4 patch values [0..15] extracted from centroid for Quantum Lab"
    )


class ArtifactReference(BaseModel):
    """Metadata describing a generated forensic visualization or data artifact."""
    artifact_id: Optional[str] = None
    artifact_type: str = Field(..., description="e.g. ELA_HEATMAP, NOISE_RESIDUAL, CMFD_MATCHES, HISTOGRAM_PLOT")
    stored_filename: str
    description: str
    mime_type: str = "image/png"
    sha256_hash: Optional[str] = None


class TechniqueResult(BaseModel):
    """Standardized output of a single forensic technique execution."""
    technique_id: str
    technique_name: str
    version: str
    category: str
    status: ForensicStatus
    execution_time_ms: float
    parameters_used: Dict[str, Any] = Field(default_factory=dict)
    observations: List[FindingItem] = Field(default_factory=list)
    indicators: List[FindingItem] = Field(default_factory=list)
    hypotheses: List[FindingItem] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    candidate_regions: List[RegionOfInterest] = Field(default_factory=list)
    artifacts: List[ArtifactReference] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class TechniqueDescriptor(BaseModel):
    """Catalog metadata describing an available forensic technique."""
    id: str
    name: str
    version: str
    category: str
    description: str
    supported_formats: List[str]
    default_parameters: Dict[str, Any]
    limitations: List[str]


class AnalysisExecutionRequest(BaseModel):
    """Request payload to trigger classical forensic analysis on an evidence item."""
    techniques: Optional[List[str]] = Field(
        None,
        description="List of technique IDs to execute. If omitted, all applicable techniques are executed."
    )
    parameters: Optional[Dict[str, Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Per-technique parameter overrides, e.g. {'ela': {'quality': 90, 'scale': 20}}"
    )


class AnalysisSummaryResponse(BaseModel):
    """Full forensic analysis summary returned by API."""
    analysis_id: str
    evidence_id: str
    case_id: Optional[str]
    status: str
    total_execution_time_ms: float
    techniques_run: int
    techniques_succeeded: int
    techniques_failed: int
    techniques_unsupported: int
    overall_status: ForensicStatus
    technique_results: Dict[str, TechniqueResult]
    consensus_regions: List[RegionOfInterest] = Field(default_factory=list)
    artifacts: List[ArtifactReference] = Field(default_factory=list)
    created_at: str

