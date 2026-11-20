"""Analysis and Artifact schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ArtifactResponse(BaseModel):
    """View schema for an analysis artifact file."""
    id: str
    analysis_id: str
    artifact_type: str
    stored_filename: str
    sha256_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    """View schema for an analysis run."""
    id: str
    case_id: Optional[str]
    evidence_id: str
    analysis_type: str
    algorithm_name: str
    status: str
    config_json: Optional[str]
    results_json: Optional[str]
    execution_time_ms: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    artifacts: List[ArtifactResponse] = []

    model_config = ConfigDict(from_attributes=True)

