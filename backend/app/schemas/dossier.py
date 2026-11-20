"""Pydantic schemas for forensic investigation dossiers, sections, previews, and exports."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DossierSectionItem(BaseModel):
    """Schema representing an individual report section."""
    id: str
    dossier_id: str
    section_key: str
    title: str
    order_index: int
    is_enabled: bool
    custom_content: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DossierSectionUpdate(BaseModel):
    """Payload to update an individual dossier section."""
    title: Optional[str] = None
    order_index: Optional[int] = None
    is_enabled: Optional[bool] = None
    custom_content: Optional[str] = None


class DossierCreate(BaseModel):
    """Payload to create a new forensic investigation dossier."""
    title: str = Field(..., max_length=255, description="Title of the forensic dossier")
    author: Optional[str] = Field(default="Lead Forensic Examiner", max_length=128)
    confidentiality_level: Optional[str] = Field(
        default="STRICTLY CONFIDENTIAL - FORENSIC EVIDENCE", max_length=64
    )
    investigation_scope: Optional[str] = Field(
        default=None, description="Scope and terms of forensic examination"
    )
    executive_summary: Optional[str] = Field(
        default=None, description="Executive narrative summary of findings"
    )
    examiner_conclusions: Optional[str] = Field(
        default=None, description="Examiner-authored professional conclusions"
    )
    recommendations: Optional[str] = Field(
        default=None, description="Actionable recommendations for claim handler or legal counsel"
    )
    limitations: Optional[str] = Field(
        default=None, description="Documented technical or physical limitations of the examination"
    )
    selected_evidence_ids: Optional[List[str]] = Field(
        default=None, description="Explicit list of evidence item IDs to include"
    )
    selected_analysis_ids: Optional[List[str]] = Field(
        default=None, description="Explicit list of classical analysis IDs to include"
    )
    selected_roi_ids: Optional[List[str]] = Field(
        default=None, description="Explicit list of Region of Interest IDs to include"
    )
    include_quantum_experiments: Optional[bool] = Field(
        default=True, description="Whether to include quantum image comparison records"
    )


class DossierUpdate(BaseModel):
    """Payload to update an existing dossier."""
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=128)
    status: Optional[str] = Field(
        None, description="DRAFT, IN_REVIEW, APPROVED, EXPORTED, SUPERSEDED"
    )
    version: Optional[int] = Field(None, ge=1)
    confidentiality_level: Optional[str] = None
    investigation_scope: Optional[str] = None
    executive_summary: Optional[str] = None
    examiner_conclusions: Optional[str] = None
    recommendations: Optional[str] = None
    limitations: Optional[str] = None
    selected_evidence_ids: Optional[List[str]] = None
    selected_analysis_ids: Optional[List[str]] = None
    selected_roi_ids: Optional[List[str]] = None
    include_quantum_experiments: Optional[bool] = None


class DossierExportResponse(BaseModel):
    """Metadata describing an exported PDF or JSON report artifact."""
    id: str
    dossier_id: str
    version: int
    export_format: str
    filename: str
    file_size: int
    sha256_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DossierResponse(BaseModel):
    """Public representation of a forensic investigation dossier."""
    id: str
    case_id: str
    dossier_number: str
    title: str
    author: str
    status: str
    version: int
    confidentiality_level: str
    investigation_scope: Optional[str] = None
    executive_summary: Optional[str] = None
    examiner_conclusions: Optional[str] = None
    recommendations: Optional[str] = None
    limitations: Optional[str] = None
    configuration_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sections: List[DossierSectionItem] = []
    latest_export: Optional[DossierExportResponse] = None
    export_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class DossierPreviewResponse(BaseModel):
    """Comprehensive structured dossier payload for live inspection and rendering."""
    dossier_id: str
    case_id: str
    case_number: str
    case_title: str
    dossier_number: str
    title: str
    author: str
    status: str
    version: int
    confidentiality_level: str
    created_at: datetime
    updated_at: datetime
    investigation_scope: str
    executive_summary: str
    examiner_conclusions: str
    recommendations: str
    limitations: str
    evidence_register: List[Dict[str, Any]]
    chain_of_custody_events: List[Dict[str, Any]]
    forensic_methodology: List[Dict[str, Any]]
    findings_categorized: Dict[str, List[Dict[str, Any]]]
    roi_evidence: List[Dict[str, Any]]
    image_comparisons: List[Dict[str, Any]]
    quantum_experiments: List[Dict[str, Any]]
    examiner_notes: List[Dict[str, Any]]
    appendices: Dict[str, Any]
    completeness_disclosure: Dict[str, Any]

