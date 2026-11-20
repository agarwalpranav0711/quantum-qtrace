/**
 * Centralized API client for Q-TRACE backend.
 * Provides typed HTTP communication with consistent error unwrapping.
 */

import {
  CaseCreate,
  CaseDetailResponse,
  CaseResponse,
  CaseUpdate,
  EvidenceResponse,
  EvidenceVerifyResponse,
  ExaminerNoteCreate,
  ExaminerNoteResponse,
  HealthResponse,
  PaginatedResponse,
  QuantumComparisonRequest,
  QuantumComparisonResponse,
  SystemInfoResponse,
  APIErrorResponse,
  TechniqueDescriptor,
  AnalysisExecutionRequest,
  AnalysisSummaryResponse,
  AnalysisHistoryItem,
  ROICreate,
  ROIUpdate,
  ROIResponse,
  ROICropResponse,
  ImageComparisonRequest,
  ImageComparisonResponse,
  DossierCreate,
  DossierUpdate,
  DossierSectionUpdate,
  DossierResponse,
  DossierSectionItem,
  DossierExportResponse,
  DossierPreviewResponse,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

class ApiError extends Error {
  code: string;
  details?: Record<string, unknown>;
  statusCode: number;

  constructor(message: string, code: string, statusCode: number, details?: Record<string, unknown>) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetails = {
      code: "HTTP_ERROR",
      message: `Request failed with status ${response.status}: ${response.statusText}`,
      details: {},
    };

    try {
      const errorJson: APIErrorResponse = await response.json();
      if (errorJson?.error) {
        errorDetails = {
          code: errorJson.error.code || "UNKNOWN_ERROR",
          message: errorJson.error.message || errorDetails.message,
          details: errorJson.error.details || {},
        };
      }
    } catch {
      // Use fallback error details if body is not JSON
    }

    throw new ApiError(errorDetails.message, errorDetails.code, response.status, errorDetails.details);
  }

  return response.json();
}

export const api = {
  // Health & System
  getHealth: (): Promise<HealthResponse> => request<HealthResponse>("/api/v1/health"),
  getSystemInfo: (): Promise<SystemInfoResponse> => request<SystemInfoResponse>("/api/v1/system/info"),

  // Cases
  getCases: (page = 1, pageSize = 20): Promise<PaginatedResponse<CaseResponse>> =>
    request<PaginatedResponse<CaseResponse>>(`/api/v1/cases?page=${page}&page_size=${pageSize}`),

  getCase: (caseId: string): Promise<CaseDetailResponse> =>
    request<CaseDetailResponse>(`/api/v1/cases/${caseId}`),

  createCase: (payload: CaseCreate): Promise<CaseResponse> =>
    request<CaseResponse>("/api/v1/cases", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateCase: (caseId: string, payload: CaseUpdate): Promise<CaseResponse> =>
    request<CaseResponse>(`/api/v1/cases/${caseId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  addNote: (caseId: string, payload: ExaminerNoteCreate): Promise<ExaminerNoteResponse> =>
    request<ExaminerNoteResponse>(`/api/v1/cases/${caseId}/notes`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Evidence
  uploadEvidence: (caseId: string, file: File): Promise<EvidenceResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return request<EvidenceResponse>(`/api/v1/cases/${caseId}/evidence`, {
      method: "POST",
      body: formData,
    });
  },

  listCaseEvidence: (caseId: string): Promise<EvidenceResponse[]> =>
    request<EvidenceResponse[]>(`/api/v1/cases/${caseId}/evidence`),

  listAllEvidence: (page = 1, pageSize = 20): Promise<PaginatedResponse<EvidenceResponse>> =>
    request<PaginatedResponse<EvidenceResponse>>(`/api/v1/evidence?page=${page}&page_size=${pageSize}`),

  getEvidence: (evidenceId: string): Promise<EvidenceResponse> =>
    request<EvidenceResponse>(`/api/v1/evidence/${evidenceId}`),

  getEvidenceFileUrl: (evidenceId: string): string =>
    `${API_BASE}/api/v1/evidence/${evidenceId}/file`,

  verifyEvidence: (evidenceId: string): Promise<EvidenceVerifyResponse> =>
    request<EvidenceVerifyResponse>(`/api/v1/evidence/${evidenceId}/verify`, {
      method: "POST",
    }),

  // Quantum Image Processing
  compareQuantumPatches: (payload: QuantumComparisonRequest): Promise<QuantumComparisonResponse> =>
    request<QuantumComparisonResponse>("/api/v1/quantum/compare", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Classical Digital Image Forensics
  getForensicTechniques: (): Promise<TechniqueDescriptor[]> =>
    request<TechniqueDescriptor[]>("/api/v1/forensics/techniques"),

  runForensicAnalysis: (
    evidenceId: string,
    payload: AnalysisExecutionRequest
  ): Promise<AnalysisSummaryResponse> =>
    request<AnalysisSummaryResponse>(`/api/v1/evidence/${evidenceId}/analyze`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getEvidenceAnalyses: (evidenceId: string): Promise<AnalysisHistoryItem[]> =>
    request<AnalysisHistoryItem[]>(`/api/v1/evidence/${evidenceId}/analyses`),

  getAnalysis: (analysisId: string): Promise<AnalysisSummaryResponse> =>
    request<AnalysisSummaryResponse>(`/api/v1/analysis/${analysisId}`),

  getArtifactFileUrl: (analysisId: string, artifactId: string): string =>
    `${API_BASE}/api/v1/analysis/${analysisId}/artifacts/${artifactId}/file`,

  // Part 6: Canvas, ROI Management, and Comparison
  createROI: (evidenceId: string, payload: ROICreate): Promise<ROIResponse> =>
    request<ROIResponse>(`/api/v1/evidence/${evidenceId}/rois`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listROIs: (evidenceId: string): Promise<ROIResponse[]> =>
    request<ROIResponse[]>(`/api/v1/evidence/${evidenceId}/rois`),

  getROI: (roiId: string): Promise<ROIResponse> =>
    request<ROIResponse>(`/api/v1/rois/${roiId}`),

  updateROI: (roiId: string, payload: ROIUpdate): Promise<ROIResponse> =>
    request<ROIResponse>(`/api/v1/rois/${roiId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteROI: (roiId: string): Promise<{ success: boolean; roi_id: string }> =>
    request<{ success: boolean; roi_id: string }>(`/api/v1/rois/${roiId}`, {
      method: "DELETE",
    }),

  cropROI: (roiId: string): Promise<ROICropResponse> =>
    request<ROICropResponse>(`/api/v1/rois/${roiId}/crop`, {
      method: "POST",
    }),

  compareImages: (payload: ImageComparisonRequest): Promise<ImageComparisonResponse> =>
    request<ImageComparisonResponse>("/api/v1/evidence/compare", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getDerivativeFileUrl: (artifactId: string): string =>
    `${API_BASE}/api/v1/derivatives/${artifactId}/file`,

  // Part 7: Forensic Investigation Dossiers and Reports
  createDossier: (caseId: string, payload: DossierCreate): Promise<DossierResponse> =>
    request<DossierResponse>(`/api/v1/cases/${caseId}/dossiers`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listCaseDossiers: (caseId: string): Promise<DossierResponse[]> =>
    request<DossierResponse[]>(`/api/v1/cases/${caseId}/dossiers`),

  getDossier: (dossierId: string): Promise<DossierResponse> =>
    request<DossierResponse>(`/api/v1/dossiers/${dossierId}`),

  updateDossier: (dossierId: string, payload: DossierUpdate): Promise<DossierResponse> =>
    request<DossierResponse>(`/api/v1/dossiers/${dossierId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteDossier: (dossierId: string): Promise<{ success: boolean; dossier_id: string }> =>
    request<{ success: boolean; dossier_id: string }>(`/api/v1/dossiers/${dossierId}`, {
      method: "DELETE",
    }),

  updateDossierSection: (
    dossierId: string,
    sectionId: string,
    payload: DossierSectionUpdate
  ): Promise<DossierSectionItem> =>
    request<DossierSectionItem>(`/api/v1/dossiers/${dossierId}/sections/${sectionId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  previewDossier: (dossierId: string): Promise<DossierPreviewResponse> =>
    request<DossierPreviewResponse>(`/api/v1/dossiers/${dossierId}/preview`),

  exportDossierPdf: (dossierId: string): Promise<DossierExportResponse> =>
    request<DossierExportResponse>(`/api/v1/dossiers/${dossierId}/export/pdf`, {
      method: "POST",
    }),

  exportDossierJson: (dossierId: string): Promise<DossierExportResponse> =>
    request<DossierExportResponse>(`/api/v1/dossiers/${dossierId}/export/json`, {
      method: "POST",
    }),

  listDossierExports: (dossierId: string): Promise<DossierExportResponse[]> =>
    request<DossierExportResponse[]>(`/api/v1/dossiers/${dossierId}/exports`),

  getDossierExportFileUrl: (dossierId: string, exportId: string): string =>
    `${API_BASE}/api/v1/dossiers/${dossierId}/exports/${exportId}/file`,
};

export { ApiError };

