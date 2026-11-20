/**
 * TypeScript API type definitions strictly mirroring FastAPI backend schemas.
 */

export interface APIErrorDetails {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface APIErrorResponse {
  error: APIErrorDetails;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  project: string;
}

export interface DatabaseStatus {
  connected: boolean;
  dialect: string;
  wal_mode: boolean;
}

export interface StorageStatus {
  root_path: string;
  accessible: boolean;
  directories_verified: boolean;
}

export interface QuantumBackendStatus {
  qiskit_version: string;
  aer_simulator_available: boolean;
  default_backend: string;
}

export interface SystemInfoResponse {
  status: string;
  project_name: string;
  version: string;
  environment: string;
  python_version: string;
  platform: string;
  database: DatabaseStatus;
  storage: StorageStatus;
  quantum: QuantumBackendStatus;
}

export type CaseStatus = "OPEN" | "IN_PROGRESS" | "CLOSED" | "ARCHIVED";

export interface ExaminerNoteCreate {
  content: string;
  author?: string;
  evidence_id?: string | null;
}

export interface ExaminerNoteResponse {
  id: string;
  case_id: string;
  evidence_id?: string | null;
  author: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CaseCreate {
  case_number: string;
  title: string;
  description?: string | null;
}

export interface CaseUpdate {
  title?: string | null;
  description?: string | null;
  status?: CaseStatus | null;
}

export interface CaseResponse {
  id: string;
  case_number: string;
  title: string;
  description?: string | null;
  status: CaseStatus;
  created_at: string;
  updated_at: string;
}

export interface CaseDetailResponse extends CaseResponse {
  evidence_count: number;
  notes: ExaminerNoteResponse[];
}

export type EvidenceStatus = "VERIFIED" | "COMPROMISED" | "PROCESSING" | "ERROR";

export interface EvidenceResponse {
  id: string;
  case_id?: string | null;
  original_filename: string;
  stored_filename: string;
  storage_path: string;
  mime_type: string;
  file_size: number;
  sha256_hash: string;
  width?: number | null;
  height?: number | null;
  status: EvidenceStatus;
  created_at: string;
}

export interface EvidenceVerifyResponse {
  evidence_id: string;
  original_filename: string;
  stored_sha256: string;
  current_sha256: string;
  is_intact: boolean;
  verified_at: string;
  status: "VERIFIED" | "COMPROMISED";
  message: string;
}

export type QuantumArchitecture = "16q" | "12q";

export interface QuantumComparisonRequest {
  patch_a: number[][]; // 4x4 matrix
  patch_b: number[][]; // 4x4 matrix
  architecture: QuantumArchitecture;
  shots?: number | null;
}

export interface QuantumComparisonResponse {
  architecture: string;
  qubits: number;
  depth: number;
  gate_count: number;
  fidelity: number;
  reconstructed_diff_map: number[][]; // 4x4 matrix
  classical_diff_map: number[][]; // 4x4 matrix
  difference_count: number;
  coverage_ratio: number;
  shots_used: number;
  execution_time_ms: number;
  identical: boolean;
}

// --- Classical Forensic Engine Types ---

export type ForensicStatus =
  | "NO_ANOMALY_DETECTED"
  | "POTENTIAL_INDICATOR_DETECTED"
  | "INCONCLUSIVE"
  | "UNSUPPORTED_INPUT"
  | "ANALYSIS_FAILED";

export type FindingCategory = "OBSERVATION" | "INDICATOR" | "HYPOTHESIS" | "CONCLUSION";

export interface FindingItem {
  category: FindingCategory;
  title: string;
  description: string;
  confidence?: number | null;
  details?: Record<string, unknown>;
}

export interface RegionOfInterest {
  roi_id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  score: number;
  contributing_techniques: string[];
  suggested_quantum_patch?: number[][] | null;
}

export interface ArtifactReference {
  artifact_id?: string | null;
  artifact_type: string;
  stored_filename: string;
  description: string;
  mime_type: string;
  sha256_hash?: string | null;
}

export interface TechniqueResult {
  technique_id: string;
  technique_name: string;
  version: string;
  category: string;
  status: ForensicStatus;
  execution_time_ms: number;
  parameters_used: Record<string, unknown>;
  observations: FindingItem[];
  indicators: FindingItem[];
  hypotheses: FindingItem[];
  metrics: Record<string, unknown>;
  candidate_regions: RegionOfInterest[];
  artifacts: ArtifactReference[];
  limitations: string[];
  warnings: string[];
  error_message?: string | null;
}

export interface TechniqueDescriptor {
  id: string;
  name: string;
  version: string;
  category: string;
  description: string;
  supported_formats: string[];
  default_parameters: Record<string, unknown>;
  limitations: string[];
}

export interface AnalysisExecutionRequest {
  techniques?: string[] | null;
  parameters?: Record<string, Record<string, unknown>>;
}

export interface AnalysisSummaryResponse {
  analysis_id: string;
  evidence_id: string;
  case_id?: string | null;
  status: string;
  total_execution_time_ms: number;
  techniques_run: number;
  techniques_succeeded: number;
  techniques_failed: number;
  techniques_unsupported: number;
  overall_status: ForensicStatus;
  technique_results: Record<string, TechniqueResult>;
  consensus_regions: RegionOfInterest[];
  artifacts: ArtifactReference[];
  created_at: string;
}

export interface AnalysisHistoryItem {
  analysis_id: string;
  evidence_id: string;
  analysis_type: string;
  algorithm_name: string;
  status: string;
  overall_status: string;
  execution_time_ms?: number | null;
  artifact_count: number;
  created_at: string;
}

// ==========================================
// Part 6: Canvas, ROI, and Image Comparison
// ==========================================

export interface ROICreate {
  roi_label: string;
  roi_type?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string;
  observation?: string | null;
  hypothesis?: string | null;
  confidence?: number | null;
  analysis_id?: string | null;
}

export interface ROIUpdate {
  roi_label?: string | null;
  x?: number | null;
  y?: number | null;
  width?: number | null;
  height?: number | null;
  color?: string | null;
  observation?: string | null;
  hypothesis?: string | null;
  confidence?: number | null;
}

export interface ROIResponse {
  id: string;
  evidence_id: string;
  analysis_id?: string | null;
  roi_label: string;
  roi_type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  observation?: string | null;
  hypothesis?: string | null;
  confidence?: number | null;
  created_at: string;
  updated_at: string;
}

export interface ROICropResponse {
  roi_id: string;
  evidence_id: string;
  artifact_id: string;
  stored_filename: string;
  sha256_hash: string;
  crop_x: number;
  crop_y: number;
  crop_width: number;
  crop_height: number;
  suggested_quantum_patch?: number[][] | null;
}

export interface ImageComparisonRequest {
  primary_evidence_id: string;
  comparison_evidence_id: string;
  align_images?: boolean;
  difference_threshold?: number;
  manual_offset_x?: number;
  manual_offset_y?: number;
}

export interface ImageComparisonResponse {
  primary_evidence_id: string;
  comparison_evidence_id: string;
  identical_dimensions: boolean;
  primary_dimensions: Record<string, number>;
  comparison_dimensions: Record<string, number>;
  alignment_performed: boolean;
  alignment_method: string;
  alignment_status: string;
  transformation_matrix?: number[][] | null;
  difference_pixel_count: number;
  difference_percentage: number;
  mean_absolute_error: number;
  root_mean_square_error: number;
  psnr_db: number;
  ssim_score: number;
  artifact_id?: string | null;
  artifact_filename?: string | null;
  suggested_quantum_patch_a?: number[][] | null;
  suggested_quantum_patch_b?: number[][] | null;
}

// ==========================================
// Part 7: Forensic Dossiers and Reports
// ==========================================

export interface DossierSectionItem {
  id: string;
  dossier_id: string;
  section_key: string;
  title: string;
  order_index: number;
  is_enabled: boolean;
  custom_content?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DossierSectionUpdate {
  title?: string;
  order_index?: number;
  is_enabled?: boolean;
  custom_content?: string | null;
}

export interface DossierCreate {
  title: string;
  author?: string;
  confidentiality_level?: string;
  investigation_scope?: string | null;
  executive_summary?: string | null;
  examiner_conclusions?: string | null;
  recommendations?: string | null;
  limitations?: string | null;
  selected_evidence_ids?: string[];
  selected_analysis_ids?: string[];
  selected_roi_ids?: string[];
  include_quantum_experiments?: boolean;
}

export interface DossierUpdate {
  title?: string | null;
  author?: string | null;
  status?: string | null;
  version?: number | null;
  confidentiality_level?: string | null;
  investigation_scope?: string | null;
  executive_summary?: string | null;
  examiner_conclusions?: string | null;
  recommendations?: string | null;
  limitations?: string | null;
  selected_evidence_ids?: string[];
  selected_analysis_ids?: string[];
  selected_roi_ids?: string[];
  include_quantum_experiments?: boolean;
}

export interface DossierExportResponse {
  id: string;
  dossier_id: string;
  version: number;
  export_format: "PDF" | "JSON" | string;
  filename: string;
  file_size: number;
  sha256_hash: string;
  created_at: string;
}

export interface DossierResponse {
  id: string;
  case_id: string;
  dossier_number: string;
  title: string;
  author: string;
  status: "DRAFT" | "IN_REVIEW" | "APPROVED" | "EXPORTED" | "SUPERSEDED" | string;
  version: number;
  confidentiality_level: string;
  investigation_scope?: string | null;
  executive_summary?: string | null;
  examiner_conclusions?: string | null;
  recommendations?: string | null;
  limitations?: string | null;
  configuration_json?: string | null;
  created_at: string;
  updated_at: string;
  sections: DossierSectionItem[];
  latest_export?: DossierExportResponse | null;
  export_count: number;
}

export interface DossierPreviewResponse {
  dossier_id: string;
  case_id: string;
  case_number: string;
  case_title: string;
  dossier_number: string;
  title: string;
  author: string;
  status: string;
  version: number;
  confidentiality_level: string;
  created_at: string;
  updated_at: string;
  investigation_scope: string;
  executive_summary: string;
  examiner_conclusions: string;
  recommendations: string;
  limitations: string;
  evidence_register: Array<{
    id: string;
    original_filename: string;
    stored_filename: string;
    mime_type: string;
    file_size: number;
    width?: number | null;
    height?: number | null;
    sha256_hash: string;
    status: string;
    created_at: string;
  }>;
  chain_of_custody_events: Array<{
    timestamp: string;
    action: string;
    actor: string;
    evidence_id: string;
    filename: string;
    result: string;
    details: string;
  }>;
  forensic_methodology: Array<{
    name: string;
    category: string;
    version: string;
    description: string;
  }>;
  findings_categorized: {
    facts: Array<{ title: string; description: string }>;
    observations: Array<{ title: string; description: string }>;
    indicators: Array<{ title: string; description: string }>;
    hypotheses: Array<{ title: string; description: string }>;
  };
  roi_evidence: Array<{
    id: string;
    evidence_id: string;
    roi_label: string;
    roi_type: string;
    x: number;
    y: number;
    width: number;
    height: number;
    color: string;
    confidence?: number | null;
    observation?: string | null;
    hypothesis?: string | null;
    crop_artifact_path?: string | null;
    crop_sha256?: string | null;
  }>;
  image_comparisons: Array<{
    analysis_id: string;
    primary_filename: string;
    comparison_filename: string;
    alignment_status: string;
    difference_pixel_count: number;
    difference_percentage: number;
    mean_absolute_error: number;
    root_mean_square_error: number;
    psnr_db: number;
    ssim_score: number;
    artifact_path?: string | null;
  }>;
  quantum_experiments: Array<{
    analysis_id: string;
    architecture: string;
    qubits: number;
    shots_used: number;
    fidelity: number;
    difference_count: number;
    execution_time_ms?: number | null;
  }>;
  examiner_notes: Array<{
    id: string;
    author: string;
    content: string;
    created_at: string;
  }>;
  appendices: Record<string, unknown>;
  completeness_disclosure: {
    evidence_included: number;
    evidence_omitted: number;
    notes: string;
  };
}




