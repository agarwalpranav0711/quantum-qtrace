import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { CommandCenterPage } from "../pages/CommandCenterPage";
import { QuantumLabPage } from "../pages/QuantumLabPage";
import { FindingsPage } from "../pages/FindingsPage";
import { AnalysisWorkspacePage } from "../pages/AnalysisWorkspacePage";
import { ForensicCanvasPage } from "../pages/ForensicCanvasPage";
import { ReportsPage } from "../pages/ReportsPage";

// Mock the API service to return controlled fixtures
vi.mock("../services/api", () => ({
  api: {
    getCases: vi.fn().mockResolvedValue({
      items: [
        {
          id: "case-1",
          case_number: "QC-2026-TEST",
          title: "Staged Bumper Claim",
          description: "Rear impact audit",
          status: "OPEN",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      has_next: false,
    }),
    listAllEvidence: vi.fn().mockResolvedValue({
      items: [
        {
          id: "ev-1",
          original_filename: "bumper_dent.jpg",
          stored_filename: "hash123.jpg",
          storage_path: "storage/originals/hash123.jpg",
          mime_type: "image/jpeg",
          file_size: 204800,
          sha256_hash: "629ff194c8ea4ed67e030e817359cf450f87cb2b367481171d89bd93e98d9a1f",
          width: 800,
          height: 600,
          status: "VERIFIED",
          created_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      has_next: false,
    }),
    getForensicTechniques: vi.fn().mockResolvedValue([
      {
        id: "ela",
        name: "Error Level Analysis (ELA)",
        version: "1.0.0",
        category: "Compression Physics",
        description: "Re-compression error analysis",
        supported_formats: ["image/jpeg"],
        default_parameters: { quality: 95, scale: 15 },
        limitations: ["High contrast edges flag false positives"],
      },
      {
        id: "noise",
        name: "Sensor Noise Inconsistency Analysis",
        version: "1.0.0",
        category: "Sensor Physics",
        description: "PRNU and sensor noise variance",
        supported_formats: ["image/jpeg", "image/png"],
        default_parameters: { block_size: 16 },
        limitations: ["Deep shadows suppress noise"],
      },
    ]),
    getEvidenceAnalyses: vi.fn().mockResolvedValue([]),
    listROIs: vi.fn().mockResolvedValue([
      {
        id: "roi-1",
        evidence_id: "ev-1",
        roi_label: "Bumper Impact Crack",
        roi_type: "EXAMINER_CREATED",
        x: 100,
        y: 150,
        width: 120,
        height: 80,
        color: "#00F2FE",
        confidence: 0.9,
        observation: "High-contrast fracture line",
        hypothesis: "Physical impact deformation",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]),
    createROI: vi.fn(),
    updateROI: vi.fn(),
    deleteROI: vi.fn(),
    cropROI: vi.fn(),
    compareImages: vi.fn(),
    getEvidenceFileUrl: vi.fn().mockReturnValue("blob:http://localhost/ev-1"),
    getDerivativeFileUrl: vi.fn().mockReturnValue("blob:http://localhost/art-1"),
    listCaseDossiers: vi.fn().mockResolvedValue([
      {
        id: "dos-1",
        case_id: "case-1",
        dossier_number: "DOS-QC-2026-TEST-01",
        title: "Official Impact Claim Dossier",
        author: "Senior Inspector Vance",
        status: "DRAFT",
        version: 1,
        confidentiality_level: "STRICTLY CONFIDENTIAL",
        investigation_scope: "Evaluation of photographic claim integrity.",
        executive_summary: "Photographic evidence was audited across all forensic pipelines.",
        examiner_conclusions: "Technical indicators warrant secondary physical verification.",
        sections: [
          {
            id: "sec-1",
            dossier_id: "dos-1",
            section_key: "COVER",
            title: "Cover & Incident Identification",
            order_index: 0,
            is_enabled: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "sec-2",
            dossier_id: "dos-1",
            section_key: "EXECUTIVE_SUMMARY",
            title: "Executive Summary",
            order_index: 1,
            is_enabled: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
        latest_export: null,
        export_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]),
    getDossier: vi.fn().mockResolvedValue({
      id: "dos-1",
      case_id: "case-1",
      dossier_number: "DOS-QC-2026-TEST-01",
      title: "Official Impact Claim Dossier",
      author: "Senior Inspector Vance",
      status: "DRAFT",
      version: 1,
      confidentiality_level: "STRICTLY CONFIDENTIAL",
      investigation_scope: "Evaluation of photographic claim integrity.",
      executive_summary: "Photographic evidence was audited across all forensic pipelines.",
      examiner_conclusions: "Technical indicators warrant secondary physical verification.",
      recommendations: "Request raw camera memory card for bitstream verification.",
      limitations: "Single viewpoint photograph constraints.",
      sections: [
        {
          id: "sec-1",
          dossier_id: "dos-1",
          section_key: "COVER",
          title: "Cover & Incident Identification",
          order_index: 0,
          is_enabled: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: "sec-2",
          dossier_id: "dos-1",
          section_key: "EXECUTIVE_SUMMARY",
          title: "Executive Summary",
          order_index: 1,
          is_enabled: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      latest_export: null,
      export_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }),
    listCaseEvidence: vi.fn().mockResolvedValue([
      {
        id: "ev-1",
        original_filename: "bumper_dent.jpg",
        stored_filename: "hash123.jpg",
        storage_path: "storage/originals/hash123.jpg",
        mime_type: "image/jpeg",
        file_size: 204800,
        sha256_hash: "629ff194c8ea4ed67e030e817359cf450f87cb2b367481171d89bd93e98d9a1f",
        width: 800,
        height: 600,
        status: "VERIFIED",
        created_at: new Date().toISOString(),
      },
    ]),
    previewDossier: vi.fn().mockResolvedValue({
      dossier_id: "dos-1",
      case_id: "case-1",
      case_number: "QC-2026-TEST",
      case_title: "Staged Bumper Claim",
      dossier_number: "DOS-QC-2026-TEST-01",
      title: "Official Impact Claim Dossier",
      author: "Senior Inspector Vance",
      status: "DRAFT",
      version: 1,
      confidentiality_level: "STRICTLY CONFIDENTIAL",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      investigation_scope: "Evaluation of photographic claim integrity.",
      executive_summary: "Photographic evidence was audited across all forensic pipelines.",
      examiner_conclusions: "Technical indicators warrant secondary physical verification.",
      recommendations: "Request raw camera memory card.",
      limitations: "Single viewpoint photograph constraints.",
      evidence_register: [
        {
          id: "ev-1",
          original_filename: "bumper_dent.jpg",
          stored_filename: "hash123.jpg",
          mime_type: "image/jpeg",
          file_size: 204800,
          width: 800,
          height: 600,
          sha256_hash: "629ff194c8ea4ed67e030e817359cf450f87cb2b367481171d89bd93e98d9a1f",
          status: "VERIFIED",
          created_at: new Date().toISOString(),
        },
      ],
      chain_of_custody_events: [],
      forensic_methodology: [],
      findings_categorized: {
        facts: [{ title: "Bitstream Integrity", description: "SHA-256 verified." }],
        observations: [],
        indicators: [],
        hypotheses: [],
      },
      roi_evidence: [],
      image_comparisons: [],
      quantum_experiments: [],
      examiner_notes: [],
      appendices: {},
      completeness_disclosure: {
        evidence_included: 1,
        evidence_omitted: 0,
        notes: "All evidence included.",
      },
    }),
    exportDossierPdf: vi.fn(),
    exportDossierJson: vi.fn(),
    listDossierExports: vi.fn().mockResolvedValue([]),
    getDossierExportFileUrl: vi.fn().mockReturnValue("blob:http://localhost/rep-1"),
    getSystemInfo: vi.fn().mockResolvedValue({
      status: "operational",
      project_name: "Q-TRACE",
      version: "0.4.0",
      environment: "development",
      python_version: "3.11.9",
      platform: "Windows 11",
      database: { connected: true, dialect: "sqlite", wal_mode: true },
      storage: { root_path: "storage", accessible: true, directories_verified: true },
      quantum: { qiskit_version: "2.6.2", aer_simulator_available: true, default_backend: "AerSimulator" },
    }),
    compareQuantumPatches: vi.fn().mockResolvedValue({
      architecture: "16q",
      qubits: 16,
      depth: 38,
      gate_count: 68,
      fidelity: 1.0,
      reconstructed_diff_map: [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
      ],
      classical_diff_map: [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
      ],
      difference_count: 0,
      coverage_ratio: 1.0,
      shots_used: 1024,
      execution_time_ms: 25.4,
      identical: true,
    }),
  },
}));

describe("Workstation Page Rendering", () => {
  it("renders Command Center page with active cases list", async () => {
    render(
      <MemoryRouter>
        <CommandCenterPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Staged Bumper Claim")).toBeInTheDocument();
      expect(screen.getByText("QC-2026-TEST")).toBeInTheDocument();
    });
  });

  it("renders Quantum Laboratory with 16Q & 12Q architecture selectors", () => {
    render(
      <MemoryRouter>
        <QuantumLabPage />
      </MemoryRouter>
    );

    expect(screen.getByText("Quantum Image Processing Laboratory")).toBeInTheDocument();
    expect(screen.getByText("16-Qubit NEQR")).toBeInTheDocument();
    expect(screen.getByText("12-Qubit In-Place")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /execute quantum simulation/i })).toBeInTheDocument();
  });

  it("renders Findings Taxonomy page with 4 clear evidence categories", () => {
    render(
      <MemoryRouter>
        <FindingsPage />
      </MemoryRouter>
    );

    expect(screen.getByText("Forensic Findings & Evidence Taxonomy")).toBeInTheDocument();
    expect(screen.getByText(/Directly Observed Technical Facts/i)).toBeInTheDocument();
    expect(screen.getByText(/Algorithmic Simulation & Telemetry Outputs/i)).toBeInTheDocument();
    expect(screen.getByText(/Potential Manipulation Indicators/i)).toBeInTheDocument();
    expect(screen.getByText(/Examiner Hypotheses & Qualitative Notes/i)).toBeInTheDocument();
  });

  it("renders Classical Digital Forensics Workspace with pipeline controls", async () => {
    render(
      <MemoryRouter>
        <AnalysisWorkspacePage />
      </MemoryRouter>
    );

    expect(screen.getByText("Classical Digital Forensics Workspace")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run classical analysis/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Error Level Analysis (ELA)")).toBeInTheDocument();
      expect(screen.getByText("Sensor Noise Inconsistency Analysis")).toBeInTheDocument();
      expect(screen.getByText("bumper_dent.jpg (800×600 px, 200.0 KB)")).toBeInTheDocument();
    });
  });

  it("renders Interactive Forensic Canvas with ROI inspector and tool controls", async () => {
    render(
      <MemoryRouter>
        <ForensicCanvasPage />
      </MemoryRouter>
    );

    expect(screen.getByText("Region Inspector")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /pan/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /inspect/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /draw roi/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /select roi/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText("Bumper Impact Crack").length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/120 × 80 px/i)).toBeInTheDocument();
      expect(screen.getByText(/extract sub-region crop/i)).toBeInTheDocument();
    });
  });

  it("renders Forensic Dossier & Reporting Engine with editor, preview, and export controls", async () => {
    render(
      <MemoryRouter>
        <ReportsPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/Forensic Dossier & Reporting Engine/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /new dossier/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText(/Official Impact Claim Dossier/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/DOS-QC-2026-TEST-01/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByRole("button", { name: /export pdf dossier/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /json/i })).toBeInTheDocument();
      expect(screen.getByText(/Document Preview/i)).toBeInTheDocument();
      expect(screen.getByText(/Exports/i)).toBeInTheDocument();
    });
  });
});

