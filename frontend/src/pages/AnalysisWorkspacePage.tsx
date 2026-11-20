import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Layers,
  Cpu,
  Binary,
  Microscope,
  FileSearch,
  BarChart3,
  Fingerprint,
  Spline,
  Play,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  Clock,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Info,
} from "lucide-react";
import { api, ApiError } from "../services/api";
import {
  EvidenceResponse,
  TechniqueDescriptor,
  AnalysisSummaryResponse,
  AnalysisHistoryItem,
  TechniqueResult,
  ForensicStatus,
} from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Select } from "../components/ui/Input";
import { Tabs } from "../components/ui/Tabs";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { ForensicImageViewer } from "../components/viewer/ForensicImageViewer";

interface TechniqueConfigState {
  enabled: boolean;
  params: Record<string, any>;
}

export const AnalysisWorkspacePage: React.FC = () => {
  const navigate = useNavigate();

  // Evidence state
  const [evidenceList, setEvidenceList] = useState<EvidenceResponse[]>([]);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string>("");
  const [isLoadingEvidence, setIsLoadingEvidence] = useState<boolean>(true);

  // Technique registry & config
  const [techniques, setTechniques] = useState<TechniqueDescriptor[]>([]);
  const [techConfigs, setTechConfigs] = useState<Record<string, TechniqueConfigState>>({});

  // Execution state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisSummaryResponse | null>(null);
  const [activeTechTab, setActiveTechTab] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Historical runs
  const [historyRuns, setHistoryRuns] = useState<AnalysisHistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState<boolean>(false);

  // Load evidence list and registered techniques on mount
  useEffect(() => {
    const initData = async () => {
      try {
        const [evRes, techRes] = await Promise.all([
          api.listAllEvidence(1, 50),
          api.getForensicTechniques(),
        ]);

        setEvidenceList(evRes.items);
        if (evRes.items.length > 0) {
          setSelectedEvidenceId(evRes.items[0].id);
        }

        setTechniques(techRes);
        const initialConfigs: Record<string, TechniqueConfigState> = {};
        techRes.forEach((t) => {
          initialConfigs[t.id] = {
            enabled: true,
            params: { ...t.default_parameters },
          };
        });
        setTechConfigs(initialConfigs);
      } catch (err) {
        setErrorMessage("Failed to initialize workspace data from backend.");
      } finally {
        setIsLoadingEvidence(false);
      }
    };
    initData();
  }, []);

  // Fetch analysis history when selected evidence changes
  useEffect(() => {
    if (!selectedEvidenceId) return;
    const fetchHistory = async () => {
      setIsLoadingHistory(true);
      try {
        const runs = await api.getEvidenceAnalyses(selectedEvidenceId);
        setHistoryRuns(runs);
        if (runs.length > 0 && !currentAnalysis) {
          const latest = await api.getAnalysis(runs[0].analysis_id);
          setCurrentAnalysis(latest);
          const firstKey = Object.keys(latest.technique_results)[0];
          if (firstKey) setActiveTechTab(firstKey);
        } else if (runs.length === 0) {
          setCurrentAnalysis(null);
        }
      } catch {
        // Handled via empty history
      } finally {
        setIsLoadingHistory(false);
      }
    };
    fetchHistory();
  }, [selectedEvidenceId]);

  const selectedEvidence = evidenceList.find((e) => e.id === selectedEvidenceId);

  // Handle technique toggle
  const toggleTechnique = (techId: string) => {
    setTechConfigs((prev) => ({
      ...prev,
      [techId]: {
        ...prev[techId],
        enabled: !prev[techId]?.enabled,
      },
    }));
  };

  // Handle parameter change
  const updateParam = (techId: string, paramKey: string, val: any) => {
    setTechConfigs((prev) => ({
      ...prev,
      [techId]: {
        ...prev[techId],
        params: {
          ...prev[techId]?.params,
          [paramKey]: val,
        },
      },
    }));
  };

  // Run pipeline
  const handleExecuteAnalysis = async () => {
    if (!selectedEvidenceId) return;
    setIsAnalyzing(true);
    setErrorMessage(null);

    const enabledTechs = Object.keys(techConfigs).filter((k) => techConfigs[k].enabled);
    if (enabledTechs.length === 0) {
      setErrorMessage("Please select at least one forensic technique to execute.");
      setIsAnalyzing(false);
      return;
    }

    const paramsPayload: Record<string, Record<string, any>> = {};
    enabledTechs.forEach((k) => {
      paramsPayload[k] = techConfigs[k].params;
    });

    try {
      const result = await api.runForensicAnalysis(selectedEvidenceId, {
        techniques: enabledTechs,
        parameters: paramsPayload,
      });

      setCurrentAnalysis(result);
      const firstTech = Object.keys(result.technique_results)[0];
      if (firstTech) setActiveTechTab(firstTech);

      // Refresh history list
      const updatedHistory = await api.getEvidenceAnalyses(selectedEvidenceId);
      setHistoryRuns(updatedHistory);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Analysis execution failed. Please verify backend status.");
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Load a historical run
  const loadHistoricalRun = async (analysisId: string) => {
    setIsAnalyzing(true);
    setErrorMessage(null);
    try {
      const run = await api.getAnalysis(analysisId);
      setCurrentAnalysis(run);
      const firstTech = Object.keys(run.technique_results)[0];
      if (firstTech) setActiveTechTab(firstTech);
    } catch {
      setErrorMessage("Failed to load historical analysis.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Quantum Lab Handoff
  const handleHandoffToQuantumLab = (patch: number[][]) => {
    // Store in session storage so QuantumLabPage can read it
    sessionStorage.setItem("qtrace_handoff_patch", JSON.stringify(patch));
    navigate("/quantum-lab");
  };

  const getStatusBadge = (status: ForensicStatus) => {
    switch (status) {
      case "NO_ANOMALY_DETECTED":
        return <Badge variant="verified">NO ANOMALY DETECTED</Badge>;
      case "POTENTIAL_INDICATOR_DETECTED":
        return <Badge variant="compromised">POTENTIAL INDICATOR DETECTED</Badge>;
      case "INCONCLUSIVE":
        return <Badge variant="warning">INCONCLUSIVE</Badge>;
      case "UNSUPPORTED_INPUT":
        return <Badge variant="neutral">UNSUPPORTED INPUT</Badge>;
      case "ANALYSIS_FAILED":
        return <Badge variant="compromised">ANALYSIS FAILED</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getTechniqueIcon = (id: string) => {
    switch (id) {
      case "ela":
        return <Layers className="w-4 h-4 text-cyan-400" />;
      case "noise":
        return <Microscope className="w-4 h-4 text-emerald-400" />;
      case "copy_move":
        return <Fingerprint className="w-4 h-4 text-indigo-400" />;
      case "metadata":
        return <FileSearch className="w-4 h-4 text-amber-400" />;
      case "statistics":
        return <BarChart3 className="w-4 h-4 text-rose-400" />;
      case "perceptual_hash":
        return <Binary className="w-4 h-4 text-cyan-400" />;
      case "resampling":
        return <Spline className="w-4 h-4 text-emerald-400" />;
      default:
        return <Cpu className="w-4 h-4 text-slate-400" />;
    }
  };

  const activeResult: TechniqueResult | undefined = currentAnalysis?.technique_results[activeTechTab];

  return (
    <div className="space-y-6">
      {/* Page Title & Breadcrumb Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
          <Microscope className="w-6 h-6 text-cyan-400" />
          Classical Digital Forensics Workspace
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Execute orthogonal physical, optical, and signal analysis pipelines against preserved evidence.
          Every technique yields reproducible measurements, candidate regions, and generated artifacts.
        </p>
      </div>

      {errorMessage && (
        <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-md text-xs text-rose-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Target Evidence Selector Card */}
      <Card variant="surface">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          <div className="lg:col-span-5">
            <label htmlFor="evidence-select" className="block text-xs font-medium text-slate-300 mb-1">
              Select Target Photographic Evidence
            </label>
            {isLoadingEvidence ? (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <LoadingSpinner size="sm" /> Loading evidence catalog...
              </div>
            ) : evidenceList.length === 0 ? (
              <p className="text-xs text-amber-400">
                No evidence items found in repository. Please upload an image in the Evidence Library.
              </p>
            ) : (
              <Select
                id="evidence-select"
                value={selectedEvidenceId}
                onChange={(e) => setSelectedEvidenceId(e.target.value)}
              >
                {evidenceList.map((ev) => (
                  <option key={ev.id} value={ev.id}>
                    {ev.original_filename} ({ev.width || "?"}×{ev.height || "?"} px, {(ev.file_size / 1024).toFixed(1)} KB)
                  </option>
                ))}
              </Select>
            )}
          </div>

          {selectedEvidence && (
            <div className="lg:col-span-7 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs font-mono bg-dark-900/60 p-2.5 rounded border border-dark-700">
              <div>
                <span className="text-slate-500">MIME:</span>{" "}
                <span className="text-slate-200">{selectedEvidence.mime_type}</span>
              </div>
              <div>
                <span className="text-slate-500">SHA-256:</span>{" "}
                <span className="text-cyan-400" title={selectedEvidence.sha256_hash}>
                  {selectedEvidence.sha256_hash.slice(0, 16)}...
                </span>
              </div>
              <div>
                <span className="text-slate-500">WORM STATUS:</span>{" "}
                <span className="text-emerald-400">READ-ONLY (LOCKED)</span>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Two-Column Workspace Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left Column: Technique Configuration & Execution (5 cols) */}
        <div className="xl:col-span-5 space-y-4">
          <Card variant="surface">
            <CardHeader className="flex justify-between items-center pb-3">
              <div>
                <CardTitle>Forensic Pipeline Configuration</CardTitle>
                <CardDescription>Select orthogonal techniques to execute on this evidence</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    const allOn: Record<string, TechniqueConfigState> = {};
                    techniques.forEach((t) => {
                      allOn[t.id] = { enabled: true, params: { ...t.default_parameters } };
                    });
                    setTechConfigs(allOn);
                  }}
                >
                  Select All
                </Button>
              </div>
            </CardHeader>

            <div className="space-y-3">
              {techniques.map((t) => {
                const cfg = techConfigs[t.id] || { enabled: true, params: {} };
                return (
                  <div
                    key={t.id}
                    className={`p-3 rounded-lg border transition-all ${
                      cfg.enabled
                        ? "bg-dark-900/80 border-cyan-500/30"
                        : "bg-dark-950/40 border-dark-800 opacity-60"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-2.5">
                        <input
                          type="checkbox"
                          id={`tech-${t.id}`}
                          checked={cfg.enabled}
                          onChange={() => toggleTechnique(t.id)}
                          className="mt-1 h-4 w-4 rounded border-dark-700 bg-dark-900 text-cyan-500 focus:ring-cyan-500/30"
                        />
                        <div>
                          <label
                            htmlFor={`tech-${t.id}`}
                            className="text-xs font-semibold text-slate-200 cursor-pointer flex items-center gap-1.5"
                          >
                            {getTechniqueIcon(t.id)}
                            {t.name}
                          </label>
                          <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">{t.description}</p>
                        </div>
                      </div>
                      <Badge variant="neutral" className="text-[10px] uppercase shrink-0">
                        {t.category}
                      </Badge>
                    </div>

                    {/* Technique-specific parameters when enabled */}
                    {cfg.enabled && (
                      <div className="mt-2.5 pt-2 border-t border-dark-800/80 pl-6 text-xs space-y-2">
                        {t.id === "ela" && (
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <span className="text-[11px] text-slate-400">JPEG Quality: {cfg.params.quality || 95}</span>
                              <input
                                type="range"
                                min="50"
                                max="100"
                                value={cfg.params.quality || 95}
                                onChange={(e) => updateParam("ela", "quality", parseInt(e.target.value))}
                                className="w-full h-1 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                              />
                            </div>
                            <div>
                              <span className="text-[11px] text-slate-400">Amplification: {cfg.params.scale || 15}x</span>
                              <input
                                type="range"
                                min="5"
                                max="30"
                                value={cfg.params.scale || 15}
                                onChange={(e) => updateParam("ela", "scale", parseInt(e.target.value))}
                                className="w-full h-1 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                              />
                            </div>
                          </div>
                        )}

                        {t.id === "noise" && (
                          <div className="flex items-center gap-3">
                            <span className="text-[11px] text-slate-400">Block Size:</span>
                            <select
                              value={cfg.params.block_size || 16}
                              onChange={(e) => updateParam("noise", "block_size", parseInt(e.target.value))}
                              className="bg-dark-800 text-slate-200 text-xs rounded border border-dark-700 px-2 py-0.5"
                            >
                              <option value="16">16 × 16 px (Fine)</option>
                              <option value="32">32 × 32 px (Coarse)</option>
                            </select>
                          </div>
                        )}

                        {t.id === "copy_move" && (
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <span className="text-[11px] text-slate-400">Detector:</span>
                              <select
                                value={cfg.params.algorithm || "SIFT"}
                                onChange={(e) => updateParam("copy_move", "algorithm", e.target.value)}
                                className="w-full bg-dark-800 text-slate-200 text-xs rounded border border-dark-700 px-2 py-0.5"
                              >
                                <option value="SIFT">SIFT (Scale-Invariant)</option>
                                <option value="ORB">ORB (Fast Binary)</option>
                              </select>
                            </div>
                            <div>
                              <span className="text-[11px] text-slate-400">Ratio: {cfg.params.ratio_threshold || 0.68}</span>
                              <input
                                type="range"
                                min="0.50"
                                max="0.80"
                                step="0.02"
                                value={cfg.params.ratio_threshold || 0.68}
                                onChange={(e) => updateParam("copy_move", "ratio_threshold", parseFloat(e.target.value))}
                                className="w-full h-1 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="mt-4 pt-3 border-t border-dark-800 flex justify-between items-center">
              <span className="text-xs text-slate-400">
                {Object.values(techConfigs).filter((c) => c.enabled).length} of {techniques.length} techniques armed
              </span>
              <Button
                variant="primary"
                onClick={handleExecuteAnalysis}
                disabled={isAnalyzing || !selectedEvidenceId}
                className="gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Executing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-dark-950" />
                    <span>Run Classical Analysis</span>
                  </>
                )}
              </Button>
            </div>
          </Card>

          {/* Historical Runs Ledger */}
          <Card variant="surface">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-400">
                Previous Analysis Runs ({historyRuns.length})
              </CardTitle>
            </CardHeader>
            {isLoadingHistory ? (
              <div className="py-4 text-center text-xs text-slate-500">Loading historical runs...</div>
            ) : historyRuns.length === 0 ? (
              <div className="py-3 text-center text-xs text-slate-500 italic">No prior runs recorded for this file.</div>
            ) : (
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {historyRuns.map((run) => (
                  <button
                    key={run.analysis_id}
                    onClick={() => loadHistoricalRun(run.analysis_id)}
                    className={`w-full text-left p-2 rounded text-xs flex justify-between items-center transition-colors ${
                      currentAnalysis?.analysis_id === run.analysis_id
                        ? "bg-cyan-500/10 border border-cyan-500/40 text-cyan-300"
                        : "bg-dark-900/60 hover:bg-dark-800 text-slate-300 border border-dark-800"
                    }`}
                  >
                    <div>
                      <div className="font-mono text-[11px]">
                        {new Date(run.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                        <span className="text-slate-500 ml-2">({run.execution_time_ms ? `${run.execution_time_ms.toFixed(0)} ms` : ""})</span>
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5">{run.analysis_type}</div>
                    </div>
                    {getStatusBadge(run.overall_status as ForensicStatus)}
                  </button>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: Execution Output, Visual Artifacts & Findings (7 cols) */}
        <div className="xl:col-span-7 space-y-4">
          {!currentAnalysis ? (
            <Card variant="surface" className="py-16 text-center">
              <Microscope className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-slate-300">No Forensic Analysis Selected</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                Configure the desired forensic techniques on the left and click "Run Classical Analysis",
                or select a previously recorded run from the ledger.
              </p>
            </Card>
          ) : (
            <>
              {/* Executive Outcome Banner */}
              <Card variant="surface" className="border-l-4 border-l-cyan-500">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400 font-mono">ANALYSIS ID: {currentAnalysis.analysis_id.slice(0, 8)}...</span>
                      {getStatusBadge(currentAnalysis.overall_status)}
                    </div>
                    <div className="text-xs text-slate-300 mt-1 flex items-center gap-4 font-mono">
                      <span>Total Time: {currentAnalysis.total_execution_time_ms.toFixed(1)} ms</span>
                      <span>Methods Run: {currentAnalysis.techniques_run}</span>
                      <span>Artifacts: {currentAnalysis.artifacts.length}</span>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate(`/canvas?evidence_id=${selectedEvidenceId}`)}
                    className="text-xs py-1 px-2.5 gap-1.5 border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Inspect on Canvas</span>
                  </Button>
                </div>

                {/* Consensus Regions of Interest & Quantum Lab Bridge */}
                {currentAnalysis.consensus_regions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-dark-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-rose-400 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Consensus Regions of Interest ({currentAnalysis.consensus_regions.length})
                      </span>
                    </div>
                    <div className="space-y-2">
                      {currentAnalysis.consensus_regions.map((roi) => (
                        <div
                          key={roi.roi_id}
                          className="bg-dark-950/80 p-2.5 rounded border border-rose-500/30 flex flex-wrap items-center justify-between gap-3"
                        >
                          <div className="text-xs">
                            <span className="font-mono text-cyan-400 font-bold">{roi.roi_id}: </span>
                            <span className="text-slate-300 font-mono">
                              Box [{roi.x}, {roi.y}, {roi.width}×{roi.height} px]
                            </span>
                            <span className="text-slate-400 ml-2">Score: {(roi.score * 100).toFixed(0)}%</span>
                            <div className="text-[11px] text-slate-400 mt-0.5">
                              Contributing Methods: {roi.contributing_techniques.join(", ")}
                            </div>
                          </div>

                          {roi.suggested_quantum_patch && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => handleHandoffToQuantumLab(roi.suggested_quantum_patch!)}
                              className="text-xs py-1 px-2.5 gap-1.5 border-indigo-500/40 text-indigo-300 hover:bg-indigo-950/40"
                            >
                              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                              <span>Verify 4×4 in Quantum Lab</span>
                              <ArrowRight className="w-3 h-3" />
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>

              {/* Techniques Result Tabs */}
              <div className="border-b border-dark-700 flex gap-1 overflow-x-auto">
                {Object.keys(currentAnalysis.technique_results).map((techKey) => {
                  const res = currentAnalysis.technique_results[techKey];
                  const isActive = activeTechTab === techKey;
                  return (
                    <button
                      key={techKey}
                      onClick={() => setActiveTechTab(techKey)}
                      className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-all whitespace-nowrap ${
                        isActive
                          ? "border-cyan-400 text-cyan-400 bg-dark-900/60"
                          : "border-transparent text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {getTechniqueIcon(techKey)}
                      <span>{res.technique_name}</span>
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          res.status === "POTENTIAL_INDICATOR_DETECTED"
                            ? "bg-rose-400"
                            : res.status === "NO_ANOMALY_DETECTED"
                            ? "bg-emerald-400"
                            : "bg-slate-400"
                        }`}
                      />
                    </button>
                  );
                })}
              </div>

              {/* Active Technique Inspector */}
              {activeResult && (
                <div className="space-y-4">
                  {/* Technique Details Header */}
                  <div className="flex justify-between items-center bg-dark-900/40 p-3 rounded border border-dark-800 text-xs">
                    <div>
                      <span className="font-semibold text-slate-200">{activeResult.technique_name}</span>
                      <span className="text-slate-500 ml-2">v{activeResult.version}</span>
                      <span className="text-slate-500 ml-2 font-mono">({activeResult.execution_time_ms.toFixed(1)} ms)</span>
                    </div>
                    {getStatusBadge(activeResult.status)}
                  </div>

                  {/* Visual Artifacts Gallery (Heatmaps, CMFD Matches, Histograms) */}
                  {activeResult.artifacts.length > 0 && (
                    <Card variant="surface">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-xs uppercase tracking-wider text-slate-400">
                          Generated Forensic Artifact
                        </CardTitle>
                      </CardHeader>
                      <div className="space-y-3">
                        {activeResult.artifacts.map((art) => {
                          const fileUrl = art.artifact_id
                            ? api.getArtifactFileUrl(currentAnalysis.analysis_id, art.artifact_id)
                            : "";
                          return (
                            <div key={art.stored_filename} className="space-y-2">
                              <div className="rounded-lg overflow-hidden border border-dark-700 bg-black flex items-center justify-center min-h-[220px]">
                                {fileUrl ? (
                                  <img
                                    src={fileUrl}
                                    alt={art.description}
                                    className="max-h-[380px] w-auto object-contain mx-auto"
                                    loading="lazy"
                                  />
                                ) : (
                                  <div className="text-xs text-slate-500">Generating artifact preview...</div>
                                )}
                              </div>
                              <div className="flex justify-between items-center text-[11px] text-slate-400 px-1 font-mono">
                                <span>{art.description}</span>
                                {art.sha256_hash && (
                                  <span className="text-slate-500">SHA-256: {art.sha256_hash.slice(0, 12)}...</span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </Card>
                  )}

                  {/* Findings Taxonomy: Observations, Indicators, Hypotheses */}
                  <div className="space-y-3">
                    {/* Indicators */}
                    {activeResult.indicators.length > 0 && (
                      <div className="bg-rose-950/20 border border-rose-800/40 rounded p-3 text-xs space-y-2">
                        <span className="font-semibold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                          Forensic Indicators Flagged ({activeResult.indicators.length})
                        </span>
                        {activeResult.indicators.map((ind, idx) => (
                          <div key={idx} className="pl-5 border-l-2 border-rose-500/60 text-slate-200">
                            <div className="font-medium text-rose-200">{ind.title}</div>
                            <div className="text-slate-400 text-[11px] mt-0.5">{ind.description}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Observations */}
                    {activeResult.observations.length > 0 && (
                      <div className="bg-dark-900/60 border border-dark-800 rounded p-3 text-xs space-y-2">
                        <span className="font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Info className="w-3.5 h-3.5 text-cyan-400" />
                          Measured Observations ({activeResult.observations.length})
                        </span>
                        {activeResult.observations.map((obs, idx) => (
                          <div key={idx} className="pl-5 border-l-2 border-cyan-500/40 text-slate-200">
                            <div className="font-medium text-slate-200">{obs.title}</div>
                            <div className="text-slate-400 text-[11px] mt-0.5">{obs.description}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Hypotheses */}
                    {activeResult.hypotheses.length > 0 && (
                      <div className="bg-indigo-950/20 border border-indigo-800/40 rounded p-3 text-xs space-y-2">
                        <span className="font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                          Investigative Hypotheses ({activeResult.hypotheses.length})
                        </span>
                        {activeResult.hypotheses.map((hyp, idx) => (
                          <div key={idx} className="pl-5 border-l-2 border-indigo-500/60 text-slate-200">
                            <div className="font-medium text-indigo-200">{hyp.title}</div>
                            <div className="text-slate-400 text-[11px] mt-0.5">{hyp.description}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Numerical Metrics Summary */}
                    {Object.keys(activeResult.metrics).length > 0 && (
                      <Card variant="surface">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-xs uppercase tracking-wider text-slate-400">
                            Algorithmic Measurements
                          </CardTitle>
                        </CardHeader>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs font-mono">
                          {Object.entries(activeResult.metrics).map(([k, v]) => {
                            if (typeof v === "object" && v !== null) return null;
                            return (
                              <div key={k} className="bg-dark-950/80 p-2 rounded border border-dark-800">
                                <span className="text-slate-500 block text-[10px] uppercase truncate">{k}</span>
                                <span className="text-cyan-400 font-semibold">{String(v)}</span>
                              </div>
                            );
                          })}
                        </div>
                      </Card>
                    )}

                    {/* Scientific Limitations & Humility Warnings */}
                    {activeResult.limitations.length > 0 && (
                      <div className="bg-dark-950/90 border border-dark-800/80 rounded p-3 text-[11px] text-slate-400 space-y-1">
                        <span className="font-semibold text-slate-300 uppercase tracking-wider block mb-1">
                          Scientific Limitations & Scope of Measurement
                        </span>
                        <ul className="list-disc pl-4 space-y-1 text-slate-400">
                          {activeResult.limitations.map((lim, idx) => (
                            <li key={idx}>{lim}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
