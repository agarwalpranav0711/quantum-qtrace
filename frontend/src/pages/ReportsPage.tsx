import React, { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  FileText,
  Download,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Calendar,
  User,
  Plus,
  Save,
  Trash2,
  Eye,
  Sliders,
  Layers,
  History,
  FileCode,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Printer,
} from "lucide-react";
import { api, ApiError } from "../services/api";
import {
  CaseResponse,
  DossierResponse,
  DossierCreate,
  DossierUpdate,
  DossierPreviewResponse,
  DossierExportResponse,
  EvidenceResponse,
} from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Select, Input } from "../components/ui/Input";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { Modal } from "../components/ui/Modal";

export const ReportsPage: React.FC = () => {
  // Case & Dossier Selection
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("");
  const [dossiers, setDossiers] = useState<DossierResponse[]>([]);
  const [selectedDossierId, setSelectedDossierId] = useState<string>("");
  const [activeDossier, setActiveDossier] = useState<DossierResponse | null>(null);

  // Loading & Action States
  const [isLoadingCases, setIsLoadingCases] = useState<boolean>(true);
  const [isLoadingDossiers, setIsLoadingDossiers] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isExportingPdf, setIsExportingPdf] = useState<boolean>(false);
  const [isExportingJson, setIsExportingJson] = useState<boolean>(false);
  const [errorNotice, setErrorNotice] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Active View Tab: 'editor' | 'preview' | 'exports'
  const [activeTab, setActiveTab] = useState<"editor" | "preview" | "exports">("editor");

  // Live Preview Data
  const [previewData, setPreviewData] = useState<DossierPreviewResponse | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState<boolean>(false);

  // Export History Ledger
  const [exportHistory, setExportHistory] = useState<DossierExportResponse[]>([]);
  const [isLoadingExports, setIsLoadingExports] = useState<boolean>(false);

  // Case Evidence items (for selection checkboxes)
  const [caseEvidence, setCaseEvidence] = useState<EvidenceResponse[]>([]);

  // Create Dossier Modal State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>("");
  const [newAuthor, setNewAuthor] = useState<string>("Lead Forensic Examiner");
  const [newScope, setNewScope] = useState<string>(
    "Technical evaluation of digital claim photographs for localized image manipulation, copy-move splicing, or metadata inconsistencies."
  );

  // Active Dossier Form State
  const [formTitle, setFormTitle] = useState<string>("");
  const [formAuthor, setFormAuthor] = useState<string>("");
  const [formStatus, setFormStatus] = useState<string>("DRAFT");
  const [formScope, setFormScope] = useState<string>("");
  const [formSummary, setFormSummary] = useState<string>("");
  const [formConclusions, setFormConclusions] = useState<string>("");
  const [formRecommendations, setFormRecommendations] = useState<string>("");
  const [formLimitations, setFormLimitations] = useState<string>("");
  const [selectedEvidenceIds, setSelectedEvidenceIds] = useState<string[]>([]);

  // 1. Load All Cases
  useEffect(() => {
    async function fetchCases() {
      setIsLoadingCases(true);
      try {
        const res = await api.getCases(1, 100);
        setCases(res.items);
        if (res.items.length > 0) {
          setSelectedCaseId(res.items[0].id);
        }
      } catch (err: unknown) {
        setErrorNotice(err instanceof Error ? err.message : "Failed to load cases");
      } finally {
        setIsLoadingCases(false);
      }
    }
    fetchCases();
  }, []);

  // 2. Load Dossiers & Evidence when Case changes
  useEffect(() => {
    if (!selectedCaseId) {
      setDossiers([]);
      setSelectedDossierId("");
      setActiveDossier(null);
      setCaseEvidence([]);
      return;
    }

    async function loadCaseData() {
      setIsLoadingDossiers(true);
      setErrorNotice(null);
      try {
        const [dList, evList] = await Promise.all([
          api.listCaseDossiers(selectedCaseId),
          api.listCaseEvidence(selectedCaseId),
        ]);
        setDossiers(dList);
        setCaseEvidence(evList);

        if (dList.length > 0) {
          setSelectedDossierId(dList[0].id);
        } else {
          setSelectedDossierId("");
          setActiveDossier(null);
        }
      } catch (err: unknown) {
        setErrorNotice(err instanceof Error ? err.message : "Failed to load case dossiers");
      } finally {
        setIsLoadingDossiers(false);
      }
    }

    loadCaseData();
  }, [selectedCaseId]);

  // 3. Load Selected Dossier Details & Populate Form
  useEffect(() => {
    if (!selectedDossierId) {
      setActiveDossier(null);
      return;
    }

    async function fetchDossier() {
      try {
        const d = await api.getDossier(selectedDossierId);
        setActiveDossier(d);
        setFormTitle(d.title || "");
        setFormAuthor(d.author || "Lead Forensic Examiner");
        setFormStatus(d.status || "DRAFT");
        setFormScope(d.investigation_scope || "");
        setFormSummary(d.executive_summary || "");
        setFormConclusions(d.examiner_conclusions || "");
        setFormRecommendations(d.recommendations || "");
        setFormLimitations(d.limitations || "");

        // Parse config for selected evidence
        if (d.configuration_json) {
          try {
            const cfg = JSON.parse(d.configuration_json);
            setSelectedEvidenceIds(cfg.selected_evidence_ids || []);
          } catch {
            setSelectedEvidenceIds([]);
          }
        } else {
          setSelectedEvidenceIds([]);
        }
      } catch (err: unknown) {
        setErrorNotice(err instanceof Error ? err.message : "Failed to load dossier details");
      }
    }

    fetchDossier();
  }, [selectedDossierId]);

  // 4. Fetch Live Preview when Preview tab is clicked
  const handleLoadPreview = async () => {
    if (!selectedDossierId) return;
    setIsLoadingPreview(true);
    setErrorNotice(null);
    try {
      const p = await api.previewDossier(selectedDossierId);
      setPreviewData(p);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to compile dossier preview");
    } finally {
      setIsLoadingPreview(false);
    }
  };

  // 5. Fetch Export History when Exports tab is clicked
  const handleLoadExports = async () => {
    if (!selectedDossierId) return;
    setIsLoadingExports(true);
    try {
      const expList = await api.listDossierExports(selectedDossierId);
      setExportHistory(expList);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to load export history");
    } finally {
      setIsLoadingExports(false);
    }
  };

  useEffect(() => {
    if (activeTab === "preview") {
      handleLoadPreview();
    } else if (activeTab === "exports") {
      handleLoadExports();
    }
  }, [activeTab, selectedDossierId]);

  // Handle Create Dossier
  const handleCreateDossier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCaseId) return;
    setErrorNotice(null);
    try {
      const payload: DossierCreate = {
        title: newTitle || `Forensic Dossier: ${new Date().toLocaleDateString()}`,
        author: newAuthor || "Lead Forensic Examiner",
        investigation_scope: newScope,
        selected_evidence_ids: caseEvidence.map((e) => e.id),
      };
      const created = await api.createDossier(selectedCaseId, payload);
      setDossiers((prev) => [created, ...prev]);
      setSelectedDossierId(created.id);
      setIsCreateModalOpen(false);
      setNewTitle("");
      setSuccessNotice(`Dossier "${created.dossier_number}" created successfully.`);
      setTimeout(() => setSuccessNotice(null), 3500);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to create dossier");
    }
  };

  // Handle Save Dossier Form
  const handleSaveDossier = async () => {
    if (!selectedDossierId) return;
    setIsSaving(true);
    setErrorNotice(null);
    try {
      const payload: DossierUpdate = {
        title: formTitle,
        author: formAuthor,
        status: formStatus,
        investigation_scope: formScope,
        executive_summary: formSummary,
        examiner_conclusions: formConclusions,
        recommendations: formRecommendations,
        limitations: formLimitations,
        selected_evidence_ids: selectedEvidenceIds,
      };
      const updated = await api.updateDossier(selectedDossierId, payload);
      setActiveDossier(updated);
      setDossiers((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
      setSuccessNotice("Dossier changes saved successfully.");
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to save dossier changes");
    } finally {
      setIsSaving(false);
    }
  };

  // Handle Export Official PDF
  const handleExportPdf = async () => {
    if (!selectedDossierId) return;
    setIsExportingPdf(true);
    setErrorNotice(null);
    try {
      const exp = await api.exportDossierPdf(selectedDossierId);
      setSuccessNotice(
        `PDF Dossier "${exp.filename}" generated successfully! SHA-256: ${exp.sha256_hash.substring(0, 16)}...`
      );
      // Trigger download
      window.open(api.getDossierExportFileUrl(selectedDossierId, exp.id), "_blank");
      handleLoadExports();
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to generate PDF export");
    } finally {
      setIsExportingPdf(false);
    }
  };

  // Handle Export JSON
  const handleExportJson = async () => {
    if (!selectedDossierId) return;
    setIsExportingJson(true);
    setErrorNotice(null);
    try {
      const exp = await api.exportDossierJson(selectedDossierId);
      setSuccessNotice(`JSON Dossier "${exp.filename}" exported successfully.`);
      window.open(api.getDossierExportFileUrl(selectedDossierId, exp.id), "_blank");
      handleLoadExports();
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to export JSON");
    } finally {
      setIsExportingJson(false);
    }
  };

  // Toggle evidence selection in config
  const toggleEvidenceSelection = (evId: string) => {
    setSelectedEvidenceIds((prev) =>
      prev.includes(evId) ? prev.filter((id) => id !== evId) : [...prev, evId]
    );
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification Banners */}
      {errorNotice && (
        <div className="p-3 bg-red-950/90 border border-red-800 text-red-200 text-xs rounded-lg shadow-xl flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1">{errorNotice}</div>
          <button type="button" onClick={() => setErrorNotice(null)} className="text-red-400 font-bold">
            ×
          </button>
        </div>
      )}

      {successNotice && (
        <div className="p-3 bg-cyan-950/90 border border-cyan-800 text-cyan-200 text-xs rounded-lg shadow-xl flex items-start gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div className="flex-1">{successNotice}</div>
          <button type="button" onClick={() => setSuccessNotice(null)} className="text-cyan-400 font-bold">
            ×
          </button>
        </div>
      )}

      {/* TOP HEADER: CASE & DOSSIER SELECTORS */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 bg-dark-900 border border-dark-800 rounded-lg">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-slate-100 tracking-tight">
              Forensic Dossier &amp; Reporting Engine
            </h2>
            <Badge variant="cyan" size="sm">
              Part 7
            </Badge>
          </div>
          <p className="text-xs text-slate-400">
            Generate, customize, and export court-admissible forensic dossiers linking WORM bitstreams, SIFT difference heatmaps, and quantum simulation telemetry.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Case Selector */}
          <div className="flex items-center gap-1.5 text-xs text-slate-300">
            <span className="text-[11px] font-mono text-slate-500 uppercase">Case:</span>
            <select
              value={selectedCaseId}
              onChange={(e) => setSelectedCaseId(e.target.value)}
              className="bg-dark-950 border border-dark-750 text-xs text-slate-200 rounded px-2.5 py-1.5 max-w-[200px] truncate focus:outline-none focus:border-cyan-500"
            >
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.case_number} — {c.title}
                </option>
              ))}
            </select>
          </div>

          {/* Dossier Selector */}
          <div className="flex items-center gap-1.5 text-xs text-slate-300">
            <span className="text-[11px] font-mono text-slate-500 uppercase">Dossier:</span>
            <select
              value={selectedDossierId}
              onChange={(e) => setSelectedDossierId(e.target.value)}
              disabled={dossiers.length === 0}
              className="bg-dark-950 border border-dark-750 text-xs text-slate-200 rounded px-2.5 py-1.5 max-w-[220px] truncate focus:outline-none focus:border-cyan-500 disabled:opacity-50"
            >
              {dossiers.length === 0 ? (
                <option value="">No Dossiers Created</option>
              ) : (
                dossiers.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.dossier_number} ({d.version ? `v${d.version}` : ""}) — {d.title}
                  </option>
                ))
              )}
            </select>
          </div>

          <Button
            size="sm"
            onClick={() => setIsCreateModalOpen(true)}
            className="text-xs gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Dossier</span>
          </Button>
        </div>
      </div>

      {/* DOSSIER WORKSTATION BODY */}
      {!selectedDossierId || !activeDossier ? (
        <Card variant="surface" className="py-16 text-center">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-slate-300">No Forensic Dossier Selected</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            Select an existing dossier from the selector above, or create a new formal investigation dossier to assemble findings.
          </p>
          <Button size="sm" onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-3.5 h-3.5 mr-1" />
            Create Dossier for this Investigation
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Dossier Sub-Header & Export Controls Bar */}
          <div className="p-3 bg-dark-900 border border-dark-800 rounded-lg flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs text-cyan-400 font-bold">
                {activeDossier.dossier_number}
              </span>
              <span className="text-xs font-semibold text-slate-200">
                {activeDossier.title}
              </span>
              <Badge variant={activeDossier.status === "EXPORTED" ? "verified" : "cyan"} size="sm">
                {activeDossier.status} &bull; v{activeDossier.version}
              </Badge>
            </div>

            {/* View Tabs & Export Buttons */}
            <div className="flex items-center gap-2">
              <div className="flex items-center bg-dark-950 p-1 rounded-lg border border-dark-800 text-xs">
                <button
                  type="button"
                  onClick={() => setActiveTab("editor")}
                  className={`px-3 py-1 rounded transition-colors ${
                    activeTab === "editor"
                      ? "bg-cyan-500/20 text-cyan-400 font-semibold"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Editor &amp; Scope
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("preview")}
                  className={`flex items-center gap-1 px-3 py-1 rounded transition-colors ${
                    activeTab === "preview"
                      ? "bg-cyan-500/20 text-cyan-400 font-semibold"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Document Preview</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("exports")}
                  className={`flex items-center gap-1 px-3 py-1 rounded transition-colors ${
                    activeTab === "exports"
                      ? "bg-cyan-500/20 text-cyan-400 font-semibold"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <History className="w-3.5 h-3.5" />
                  <span>Exports ({activeDossier.export_count})</span>
                </button>
              </div>

              {/* Direct Export Buttons */}
              <Button
                size="sm"
                variant="outline"
                onClick={handleExportJson}
                disabled={isExportingJson}
                className="text-xs border-dark-750 text-slate-300 hover:text-cyan-400"
                title="Export Structured JSON Dossier"
              >
                <FileCode className="w-3.5 h-3.5 mr-1" />
                <span>{isExportingJson ? "Exporting..." : "JSON"}</span>
              </Button>

              <Button
                size="sm"
                onClick={handleExportPdf}
                disabled={isExportingPdf}
                className="text-xs bg-cyan-600 hover:bg-cyan-500 text-dark-950 font-bold shadow-md"
                title="Generate Multi-Page Official PDF Dossier"
              >
                {isExportingPdf ? (
                  <>
                    <LoadingSpinner size="sm" className="w-3.5 h-3.5 mr-1" />
                    <span>Compiling PDF...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-3.5 h-3.5 mr-1" />
                    <span>Export PDF Dossier</span>
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* TAB 1: DOSSIER EDITOR & EVIDENCE CONFIGURATION */}
          {activeTab === "editor" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Narrative Fields (2 cols) */}
              <div className="lg:col-span-2 space-y-4">
                <Card variant="surface" className="p-4 space-y-4">
                  <div className="flex items-center justify-between border-b border-dark-800 pb-3">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">
                      Dossier Narrative &amp; Conclusions
                    </h3>
                    <Button
                      size="sm"
                      onClick={handleSaveDossier}
                      disabled={isSaving}
                      className="text-xs"
                    >
                      <Save className="w-3.5 h-3.5 mr-1" />
                      <span>{isSaving ? "Saving..." : "Save Dossier Changes"}</span>
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                        Dossier Title
                      </label>
                      <input
                        type="text"
                        value={formTitle}
                        onChange={(e) => setFormTitle(e.target.value)}
                        className="w-full bg-dark-950 border border-dark-750 rounded px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                        Lead Forensic Examiner
                      </label>
                      <input
                        type="text"
                        value={formAuthor}
                        onChange={(e) => setFormAuthor(e.target.value)}
                        className="w-full bg-dark-950 border border-dark-750 rounded px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                      Investigation Scope &amp; Mandate
                    </label>
                    <textarea
                      rows={2}
                      value={formScope}
                      onChange={(e) => setFormScope(e.target.value)}
                      placeholder="Examination terms, boundaries, and specific questions..."
                      className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                    />
                  </div>

                  <div>
                    <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                      Executive Narrative Summary
                    </label>
                    <textarea
                      rows={3}
                      value={formSummary}
                      onChange={(e) => setFormSummary(e.target.value)}
                      placeholder="High-level synthesis of evidence and overall findings..."
                      className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                    />
                  </div>

                  <div>
                    <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                      Examiner Conclusions
                    </label>
                    <textarea
                      rows={3}
                      value={formConclusions}
                      onChange={(e) => setFormConclusions(e.target.value)}
                      placeholder="Professional forensic interpretation distinguishing facts from indicators..."
                      className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                        Actionable Recommendations
                      </label>
                      <textarea
                        rows={2}
                        value={formRecommendations}
                        onChange={(e) => setFormRecommendations(e.target.value)}
                        placeholder="Next steps for claim investigators or surveyors..."
                        className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                      />
                    </div>

                    <div>
                      <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                        Documented Technical Limitations
                      </label>
                      <textarea
                        rows={2}
                        value={formLimitations}
                        onChange={(e) => setFormLimitations(e.target.value)}
                        placeholder="Resolution limits, compression boundaries, lighting constraints..."
                        className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                      />
                    </div>
                  </div>
                </Card>
              </div>

              {/* Right Column: Evidence Selection & Sections (1 col) */}
              <div className="space-y-4">
                {/* Evidence Inclusions Card */}
                <Card variant="surface" className="p-4 space-y-3">
                  <div className="flex items-center justify-between border-b border-dark-800 pb-2">
                    <span className="text-xs font-mono uppercase text-slate-300 font-semibold">
                      Included Evidence ({selectedEvidenceIds.length}/{caseEvidence.length})
                    </span>
                    <button
                      type="button"
                      onClick={() =>
                        setSelectedEvidenceIds(
                          selectedEvidenceIds.length === caseEvidence.length
                            ? []
                            : caseEvidence.map((e) => e.id)
                        )
                      }
                      className="text-[10px] text-cyan-400 hover:underline"
                    >
                      {selectedEvidenceIds.length === caseEvidence.length ? "Deselect All" : "Select All"}
                    </button>
                  </div>

                  <div className="space-y-1.5 max-h-56 overflow-y-auto">
                    {caseEvidence.map((ev) => {
                      const isChecked =
                        selectedEvidenceIds.length === 0 || selectedEvidenceIds.includes(ev.id);
                      return (
                        <label
                          key={ev.id}
                          className="flex items-center gap-2 p-2 rounded bg-dark-950 border border-dark-800 text-xs cursor-pointer hover:border-dark-700"
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleEvidenceSelection(ev.id)}
                            className="rounded bg-dark-900 border-dark-700 text-cyan-500 focus:ring-0"
                          />
                          <div className="flex-1 truncate">
                            <span className="font-medium text-slate-200 block truncate">
                              {ev.original_filename}
                            </span>
                            <span className="text-[10px] font-mono text-slate-500 truncate block">
                              SHA: {ev.sha256_hash.substring(0, 16)}...
                            </span>
                          </div>
                        </label>
                      );
                    })}
                  </div>
                </Card>

                {/* Report Sections Structure Card */}
                <Card variant="surface" className="p-4 space-y-2">
                  <span className="text-xs font-mono uppercase text-slate-300 font-semibold block border-b border-dark-800 pb-2">
                    Report Section Structure (13 Standard Sections)
                  </span>

                  <div className="space-y-1 text-xs">
                    {activeDossier.sections.map((sec, idx) => (
                      <div
                        key={sec.id}
                        className="flex items-center justify-between p-1.5 rounded bg-dark-950/60 border border-dark-800 text-[11px]"
                      >
                        <span className="text-slate-300 truncate">
                          {idx + 1}. {sec.title}
                        </span>
                        <span className="text-[9px] font-mono text-emerald-400">ACTIVE</span>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* TAB 2: LIVE STRUCTURED DOCUMENT PREVIEW */}
          {activeTab === "preview" && (
            <Card variant="surface" className="p-6 space-y-6 max-w-4xl mx-auto border border-dark-750">
              {isLoadingPreview ? (
                <div className="py-20 text-center">
                  <LoadingSpinner size="lg" label="Compiling live forensic dossier preview..." />
                </div>
              ) : !previewData ? (
                <div className="py-12 text-center text-slate-500">
                  <p>Unable to compile preview.</p>
                </div>
              ) : (
                <div className="space-y-6 text-xs text-slate-200">
                  {/* PREVIEW: COVER BANNER */}
                  <div className="p-6 rounded bg-dark-950 border-2 border-cyan-500/40 space-y-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-cyan-400 font-mono text-xs font-bold uppercase tracking-widest block">
                          Q-TRACE FORENSIC INVESTIGATION DOSSIER
                        </span>
                        <h1 className="text-xl font-bold text-slate-100 mt-1">{previewData.title}</h1>
                        <p className="text-xs text-slate-400 mt-0.5">
                          Associated Case: <strong className="text-cyan-300">{previewData.case_title}</strong> ({previewData.case_number})
                        </p>
                      </div>

                      <Badge variant="verified">
                        {previewData.status} &bull; v{previewData.version}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-dark-800 font-mono text-[11px]">
                      <div>
                        <span className="text-slate-500 block text-[9px]">DOSSIER REF</span>
                        <span className="text-cyan-300 font-bold">{previewData.dossier_number}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[9px]">LEAD EXAMINER</span>
                        <span className="text-slate-200">{previewData.author}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[9px]">GENERATED</span>
                        <span className="text-slate-200">{new Date(previewData.created_at).toLocaleDateString()}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[9px]">CLASSIFICATION</span>
                        <span className="text-amber-400 font-bold">{previewData.confidentiality_level}</span>
                      </div>
                    </div>
                  </div>

                  {/* SECTION 1: EXECUTIVE SUMMARY */}
                  <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-2">
                    <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                      1. Executive Summary
                    </h3>
                    <p className="text-slate-300 leading-relaxed text-[11px]">
                      {previewData.executive_summary}
                    </p>
                  </div>

                  {/* SECTION 2: INVESTIGATION SCOPE */}
                  <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-2">
                    <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                      2. Investigation Scope &amp; Mandate
                    </h3>
                    <p className="text-slate-300 leading-relaxed text-[11px]">
                      {previewData.investigation_scope}
                    </p>
                    {previewData.limitations && (
                      <p className="text-slate-400 text-[10px] italic pt-1">
                        Limitations: {previewData.limitations}
                      </p>
                    )}
                  </div>

                  {/* SECTION 3: EVIDENCE REGISTER */}
                  <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-3">
                    <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                      3. Evidence Register &amp; Cryptographic Integrity ({previewData.evidence_register.length} Files)
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left font-mono text-[11px]">
                        <thead>
                          <tr className="border-b border-dark-800 text-slate-500 text-[10px]">
                            <th className="py-1">FILENAME</th>
                            <th className="py-1">DIMENSIONS / SIZE</th>
                            <th className="py-1">NIST FIPS 180-4 SHA-256 DIGEST</th>
                            <th className="py-1">INTEGRITY</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-dark-800/60">
                          {previewData.evidence_register.map((ev) => (
                            <tr key={ev.id}>
                              <td className="py-2 text-slate-200 font-sans font-medium">{ev.original_filename}</td>
                              <td className="py-2 text-slate-400">
                                {ev.width}×{ev.height} px ({Math.round(ev.file_size / 1024)} KB)
                              </td>
                              <td className="py-2 text-cyan-400 font-mono text-[10px]">{ev.sha256_hash}</td>
                              <td className="py-2">
                                <Badge variant="verified" size="sm">
                                  {ev.status}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* SECTION 4: STRUCTURED FINDINGS */}
                  <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-3">
                    <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                      4. Structured Forensic Findings &amp; Observations
                    </h3>

                    {Object.entries(previewData.findings_categorized).map(([catKey, items]) => {
                      if (items.length === 0) return null;
                      const catTitle =
                        catKey === "facts"
                          ? "Directly Observed Technical Facts"
                          : catKey === "observations"
                          ? "Measured Algorithmic Telemetry"
                          : catKey === "indicators"
                          ? "Potential Manipulation Indicators"
                          : "Investigative Hypotheses";
                      return (
                        <div key={catKey} className="space-y-1 pt-1">
                          <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
                            {catTitle} ({items.length})
                          </span>
                          <div className="space-y-1">
                            {items.map((it, idx) => (
                              <div
                                key={idx}
                                className="p-2 rounded bg-dark-900 border border-dark-800 text-[11px] flex items-start gap-2"
                              >
                                <span className="text-cyan-400 font-bold">&bull;</span>
                                <div>
                                  <strong className="text-slate-200">{it.title}: </strong>
                                  <span className="text-slate-300">{it.description}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* SECTION 5: REGIONS OF INTEREST */}
                  <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-3">
                    <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                      5. Regions of Interest &amp; Derivative Evidence ({previewData.roi_evidence.length})
                    </h3>

                    {previewData.roi_evidence.length === 0 ? (
                      <p className="text-slate-500 italic">No specific regions recorded for this dossier.</p>
                    ) : (
                      <div className="space-y-2">
                        {previewData.roi_evidence.map((r) => (
                          <div
                            key={r.id}
                            className="p-3 rounded bg-dark-900 border border-dark-800 flex flex-wrap items-center justify-between gap-3 text-xs"
                          >
                            <div className="space-y-1 max-w-lg">
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-slate-200">{r.roi_label}</span>
                                <Badge variant="neutral" size="sm">
                                  {r.roi_type}
                                </Badge>
                                {r.confidence && (
                                  <span className="text-cyan-400 font-mono text-[10px]">
                                    Confidence: {Math.round(r.confidence * 100)}%
                                  </span>
                                )}
                              </div>
                              <div className="font-mono text-[10px] text-slate-400">
                                Coordinates: [{r.x}, {r.y}] &bull; Size: {r.width}×{r.height} px
                              </div>
                              {r.observation && (
                                <p className="text-slate-300 text-[11px]">
                                  <b>Fact:</b> {r.observation}
                                </p>
                              )}
                              {r.hypothesis && (
                                <p className="text-slate-400 text-[11px]">
                                  <b>Hypothesis:</b> {r.hypothesis}
                                </p>
                              )}
                            </div>

                            {r.crop_artifact_path && (
                              <div className="text-center font-mono text-[9px] text-slate-500">
                                <span className="px-1.5 py-0.5 rounded bg-dark-950 border border-dark-750 text-cyan-400">
                                  LOSSLESS CROP ATTACHED
                                </span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* SECTION 6: SIFT HOMOGRAPHY COMPARISONS */}
                  {previewData.image_comparisons.length > 0 && (
                    <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-3">
                      <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                        6. SIFT Homography Image Comparisons ({previewData.image_comparisons.length})
                      </h3>
                      <div className="space-y-2">
                        {previewData.image_comparisons.map((c, cIdx) => (
                          <div key={cIdx} className="p-3 rounded bg-dark-900 border border-dark-800 text-xs space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-slate-200">
                                {c.primary_filename} vs {c.comparison_filename}
                              </span>
                              <Badge variant="verified" size="sm">
                                {c.alignment_status}
                              </Badge>
                            </div>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[10px] bg-dark-950 p-2 rounded border border-dark-800">
                              <div>
                                <span className="text-slate-500 block">DELTA PIXELS</span>
                                <span className="text-slate-200 font-bold">{c.difference_pixel_count.toLocaleString()}</span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">DELTA RATIO</span>
                                <span className="text-cyan-400 font-bold">{c.difference_percentage.toFixed(2)}%</span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">MAE / RMSE</span>
                                <span className="text-slate-200">{c.mean_absolute_error.toFixed(1)} / {c.root_mean_square_error.toFixed(1)}</span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">PSNR / SSIM</span>
                                <span className="text-slate-200">{c.psnr_db.toFixed(1)} dB / {c.ssim_score.toFixed(3)}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* SECTION 7: EXAMINER CONCLUSIONS */}
                  <div className="p-4 rounded bg-dark-950 border border-dark-800 space-y-2">
                    <h3 className="font-semibold text-slate-100 text-xs uppercase tracking-wider text-cyan-400">
                      7. Examiner Conclusions &amp; Recommendations
                    </h3>
                    <p className="text-slate-300 leading-relaxed text-[11px]">
                      {previewData.examiner_conclusions}
                    </p>
                    {previewData.recommendations && (
                      <p className="text-cyan-300 text-[11px] pt-1">
                        <b>Actionable Recommendations:</b> {previewData.recommendations}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </Card>
          )}

          {/* TAB 3: EXPORT VERSION HISTORY LEDGER */}
          {activeTab === "exports" && (
            <Card variant="surface" className="p-4 space-y-4">
              <div className="flex items-center justify-between border-b border-dark-800 pb-3">
                <div>
                  <h3 className="text-xs font-mono uppercase tracking-wider text-slate-200 font-semibold">
                    Immutable Export History &amp; Cryptographic Manifests
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Every exported report version is frozen on disk, hashed via SHA-256, and retained in the permanent audit ledger.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline" onClick={handleExportJson} disabled={isExportingJson}>
                    Export JSON
                  </Button>
                  <Button size="sm" onClick={handleExportPdf} disabled={isExportingPdf}>
                    Export PDF
                  </Button>
                </div>
              </div>

              {isLoadingExports ? (
                <div className="py-12 text-center">
                  <LoadingSpinner size="md" label="Loading version history..." />
                </div>
              ) : exportHistory.length === 0 ? (
                <div className="py-12 text-center text-slate-500 text-xs">
                  No exported reports generated yet. Click "Export PDF Dossier" above to produce your first frozen edition.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left font-mono text-[11px]">
                    <thead>
                      <tr className="border-b border-dark-800 text-slate-500 text-[10px]">
                        <th className="py-2">VERSION</th>
                        <th className="py-2">FORMAT</th>
                        <th className="py-2">FILENAME / SIZE</th>
                        <th className="py-2">SHA-256 BITSTREAM HASH</th>
                        <th className="py-2">TIMESTAMP</th>
                        <th className="py-2 text-right">ACTION</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-800/60">
                      {exportHistory.map((exp) => (
                        <tr key={exp.id} className="hover:bg-dark-900/50">
                          <td className="py-2.5 font-bold text-cyan-400">v{exp.version}</td>
                          <td className="py-2.5">
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-dark-900 border border-dark-750 text-slate-300 font-semibold">
                              {exp.export_format}
                            </span>
                          </td>
                          <td className="py-2.5 text-slate-200 font-sans">
                            {exp.filename}
                            <span className="text-[10px] text-slate-500 font-mono ml-2">
                              ({Math.round(exp.file_size / 1024)} KB)
                            </span>
                          </td>
                          <td className="py-2.5 text-cyan-400 font-mono text-[10px]">{exp.sha256_hash}</td>
                          <td className="py-2.5 text-slate-400 text-[10px]">
                            {new Date(exp.created_at).toLocaleString()}
                          </td>
                          <td className="py-2.5 text-right">
                            <a
                              href={api.getDossierExportFileUrl(selectedDossierId, exp.id)}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-dark-900 border border-dark-750 text-xs text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-500/40 transition-colors"
                            >
                              <Download className="w-3 h-3" />
                              <span>Download</span>
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {/* CREATE NEW DOSSIER MODAL */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Forensic Investigation Dossier"
      >
        <form onSubmit={handleCreateDossier} className="space-y-4 text-xs">
          <div>
            <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
              Dossier Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Formal Examination Dossier: Rear Panel Claim"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
              Lead Examiner / Author
            </label>
            <input
              type="text"
              value={newAuthor}
              onChange={(e) => setNewAuthor(e.target.value)}
              className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
              Initial Investigation Scope
            </label>
            <textarea
              rows={3}
              value={newScope}
              onChange={(e) => setNewScope(e.target.value)}
              className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
            />
          </div>

          <div className="pt-3 border-t border-dark-800 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm">
              Create Dossier
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
