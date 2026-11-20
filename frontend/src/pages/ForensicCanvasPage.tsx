import React, { useEffect, useState, useMemo } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import {
  Layers,
  Crosshair,
  Move,
  Square,
  MousePointer,
  Crop,
  Cpu,
  Trash2,
  Save,
  CheckCircle2,
  AlertTriangle,
  Sliders,
  SplitSquareVertical,
  Blend,
  FileDiff,
  Eye,
  EyeOff,
  RefreshCw,
  Info,
  Sparkles,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { api, ApiError } from "../services/api";
import {
  EvidenceResponse,
  ROIResponse,
  ROICreate,
  ROIUpdate,
  ROICropResponse,
  ImageComparisonResponse,
  AnalysisSummaryResponse,
} from "../types/api";
import {
  ForensicCanvas,
  CanvasTool,
  CanvasViewMode,
  PixelSample,
  CandidateRegionOverlay,
} from "../components/canvas/ForensicCanvas";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Select, Input } from "../components/ui/Input";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const ForensicCanvasPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // URL state
  const initialEvidenceId = searchParams.get("evidence_id") || "";
  const initialCompareWith = searchParams.get("compare_with") || "";

  // Evidence Selection
  const [evidenceList, setEvidenceList] = useState<EvidenceResponse[]>([]);
  const [primaryId, setPrimaryId] = useState<string>(initialEvidenceId);
  const [comparisonId, setComparisonId] = useState<string>(initialCompareWith);
  const [isLoadingEvidence, setIsLoadingEvidence] = useState<boolean>(true);

  // Active Tool & View Modes
  const [toolMode, setToolMode] = useState<CanvasTool>("pan");
  const [viewMode, setViewMode] = useState<CanvasViewMode>("single");
  const [splitPosition, setSplitPosition] = useState<number>(50);
  const [overlayOpacity, setOverlayOpacity] = useState<number>(0.5);
  const [showAnnotations, setShowAnnotations] = useState<boolean>(true);
  const [showCandidates, setShowCandidates] = useState<boolean>(true);

  // ROIs & Overlays
  const [rois, setRois] = useState<ROIResponse[]>([]);
  const [selectedRoi, setSelectedRoi] = useState<ROIResponse | null>(null);
  const [candidateRegions, setCandidateRegions] = useState<CandidateRegionOverlay[]>([]);
  const [isLoadingRois, setIsLoadingRois] = useState<boolean>(false);

  // ROI Editor Form State
  const [editLabel, setEditLabel] = useState<string>("");
  const [editColor, setEditColor] = useState<string>("#00F2FE");
  const [editConfidence, setEditConfidence] = useState<number>(0.85);
  const [editObservation, setEditObservation] = useState<string>("");
  const [editHypothesis, setEditHypothesis] = useState<string>("");
  const [isSavingRoi, setIsSavingRoi] = useState<boolean>(false);
  const [lastCropArtifact, setLastCropArtifact] = useState<ROICropResponse | null>(null);
  const [isCropping, setIsCropping] = useState<boolean>(false);

  // Comparison State
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [alignImages, setAlignImages] = useState<boolean>(true);
  const [diffThreshold, setDiffThreshold] = useState<number>(15);
  const [comparisonResult, setComparisonResult] = useState<ImageComparisonResponse | null>(null);
  const [comparisonError, setComparisonError] = useState<string | null>(null);

  // Status Bar Live State
  const [hoverPixel, setHoverPixel] = useState<PixelSample | null>(null);
  const [currentZoom, setCurrentZoom] = useState<number>(1.0);
  const [errorNotice, setErrorNotice] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Load all available evidence items
  useEffect(() => {
    async function loadEvidence() {
      setIsLoadingEvidence(true);
      try {
        const res = await api.listAllEvidence(1, 100);
        setEvidenceList(res.items);
        if (!primaryId && res.items.length > 0) {
          setPrimaryId(res.items[0].id);
        }
      } catch (err: unknown) {
        setErrorNotice(err instanceof Error ? err.message : "Failed to load evidence items");
      } finally {
        setIsLoadingEvidence(false);
      }
    }
    loadEvidence();
  }, []);

  // Update query params when selection changes
  useEffect(() => {
    const params: Record<string, string> = {};
    if (primaryId) params.evidence_id = primaryId;
    if (comparisonId) params.compare_with = comparisonId;
    setSearchParams(params, { replace: true });
  }, [primaryId, comparisonId, setSearchParams]);

  // Load ROIs and Candidate Regions when Primary Evidence changes
  useEffect(() => {
    if (!primaryId) {
      setRois([]);
      setSelectedRoi(null);
      setCandidateRegions([]);
      return;
    }

    async function loadRoisAndAnalyses() {
      setIsLoadingRois(true);
      setErrorNotice(null);
      try {
        // 1. Fetch examiner ROIs
        const roiItems = await api.listROIs(primaryId);
        setRois(roiItems);
        if (roiItems.length > 0) {
          setSelectedRoi(roiItems[0]);
        } else {
          setSelectedRoi(null);
        }

        // 2. Fetch Part 5 analyses to load candidate regions if available
        try {
          const history = await api.getEvidenceAnalyses(primaryId);
          if (history.length > 0) {
            const latest = await api.getAnalysis(history[0].analysis_id);
            const overlays: CandidateRegionOverlay[] = [];

            // Add consensus regions
            if (latest.consensus_regions) {
              latest.consensus_regions.forEach((r, idx) => {
                overlays.push({
                  x: r.x,
                  y: r.y,
                  width: r.width,
                  height: r.height,
                  label: `Consensus Anomaly #${idx + 1}`,
                  color: "#F59E0B",
                  score: 0.9,
                });
              });
            }

            // Add technique specific candidate regions
            Object.entries(latest.technique_results || {}).forEach(([techId, res]) => {
              if (res.candidate_regions) {
                res.candidate_regions.forEach((cr, cIdx) => {
                  overlays.push({
                    x: cr.x,
                    y: cr.y,
                    width: cr.width,
                    height: cr.height,
                    label: `${techId.toUpperCase()} #${cIdx + 1}`,
                    color: techId === "ela" ? "#EC4899" : techId === "cmfd" ? "#3B82F6" : "#10B981",
                  });
                });
              }
            });

            setCandidateRegions(overlays);
          }
        } catch {
          // No previous analysis - non-blocking
        }
      } catch (err: unknown) {
        setErrorNotice(err instanceof Error ? err.message : "Failed to load ROIs");
      } finally {
        setIsLoadingRois(false);
      }
    }

    loadRoisAndAnalyses();
  }, [primaryId]);

  // Populate editor form when selected ROI changes
  useEffect(() => {
    if (selectedRoi) {
      setEditLabel(selectedRoi.roi_label || "");
      setEditColor(selectedRoi.color || "#00F2FE");
      setEditConfidence(selectedRoi.confidence !== null && selectedRoi.confidence !== undefined ? selectedRoi.confidence : 0.85);
      setEditObservation(selectedRoi.observation || "");
      setEditHypothesis(selectedRoi.hypothesis || "");
      setLastCropArtifact(null);
    }
  }, [selectedRoi]);

  // Find active evidence objects
  const primaryEvidence = useMemo(
    () => evidenceList.find((e) => e.id === primaryId),
    [evidenceList, primaryId]
  );

  const comparisonEvidence = useMemo(
    () => evidenceList.find((e) => e.id === comparisonId),
    [evidenceList, comparisonId]
  );

  // URLs
  const primarySrc = primaryId ? api.getEvidenceFileUrl(primaryId) : "";
  const comparisonSrc = comparisonId ? api.getEvidenceFileUrl(comparisonId) : "";
  const diffArtifactSrc =
    comparisonResult && comparisonResult.artifact_id
      ? api.getDerivativeFileUrl(comparisonResult.artifact_id)
      : undefined;

  // Handle Create ROI from canvas drag
  const handleCreateRoi = async (coords: { x: number; y: number; width: number; height: number }) => {
    if (!primaryId) return;
    try {
      const payload: ROICreate = {
        roi_label: `ROI #${rois.length + 1} (${coords.width}×${coords.height})`,
        roi_type: "EXAMINER_CREATED",
        x: coords.x,
        y: coords.y,
        width: coords.width,
        height: coords.height,
        color: "#00F2FE",
        confidence: 0.85,
        observation: `Inspected region at pixel (${coords.x}, ${coords.y}) measuring ${coords.width}×${coords.height} px.`,
        hypothesis: "Potential surface modification or localized discontinuity.",
      };

      const created = await api.createROI(primaryId, payload);
      setRois((prev) => [...prev, created]);
      setSelectedRoi(created);
      setToolMode("roi_select");
      setSuccessNotice(`Created Region of Interest: "${created.roi_label}"`);
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to create ROI");
    }
  };

  // Handle live ROI coordinate update from resize/drag
  const handleUpdateRoiCoords = async (
    roiId: string,
    coords: { x: number; y: number; width: number; height: number }
  ) => {
    // Optimistic local update
    setRois((prev) =>
      prev.map((r) => (r.id === roiId ? { ...r, ...coords } : r))
    );
    if (selectedRoi && selectedRoi.id === roiId) {
      setSelectedRoi((prev) => (prev ? { ...prev, ...coords } : null));
    }

    // Persist to backend
    try {
      await api.updateROI(roiId, coords);
    } catch (err: unknown) {
      console.error("Failed to persist ROI geometry:", err);
    }
  };

  // Handle Save ROI Metadata Form
  const handleSaveRoi = async () => {
    if (!selectedRoi) return;
    setIsSavingRoi(true);
    setErrorNotice(null);
    try {
      const payload: ROIUpdate = {
        roi_label: editLabel,
        color: editColor,
        confidence: editConfidence,
        observation: editObservation,
        hypothesis: editHypothesis,
      };
      const updated = await api.updateROI(selectedRoi.id, payload);
      setRois((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      setSelectedRoi(updated);
      setSuccessNotice("ROI properties saved successfully");
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to update ROI");
    } finally {
      setIsSavingRoi(false);
    }
  };

  // Handle Delete ROI
  const handleDeleteRoi = async (roiId: string) => {
    if (!window.confirm("Are you sure you want to delete this Region of Interest?")) return;
    try {
      await api.deleteROI(roiId);
      setRois((prev) => prev.filter((r) => r.id !== roiId));
      if (selectedRoi?.id === roiId) {
        setSelectedRoi(rois.find((r) => r.id !== roiId) || null);
      }
      setSuccessNotice("Region of Interest deleted");
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to delete ROI");
    }
  };

  // Handle Sub-Region Crop Extraction (Derivative Artifact)
  const handleCropRoi = async () => {
    if (!selectedRoi) return;
    setIsCropping(true);
    setErrorNotice(null);
    try {
      const cropRes = await api.cropROI(selectedRoi.id);
      setLastCropArtifact(cropRes);
      setSuccessNotice(`Cropped sub-region artifact saved with SHA-256 digest: ${cropRes.sha256_hash.substring(0, 16)}...`);
    } catch (err: unknown) {
      setErrorNotice(err instanceof Error ? err.message : "Failed to crop ROI");
    } finally {
      setIsCropping(false);
    }
  };

  // Handoff ROI 4x4 Patch to Quantum Lab
  const handleSendRoiToQuantumLab = () => {
    if (!lastCropArtifact?.suggested_quantum_patch) {
      setErrorNotice("Generate a cropped sub-region first to extract a 4×4 quantized matrix.");
      return;
    }
    sessionStorage.setItem("qtrace_handoff_patch", JSON.stringify(lastCropArtifact.suggested_quantum_patch));
    sessionStorage.setItem("qtrace_handoff_patch_a", JSON.stringify(lastCropArtifact.suggested_quantum_patch));
    navigate("/quantum-lab");
  };

  // Handle Execute Image Comparison
  const handleRunComparison = async () => {
    if (!primaryId || !comparisonId) {
      setErrorNotice("Please select both a Primary and a Comparison image.");
      return;
    }
    if (primaryId === comparisonId) {
      setErrorNotice("Please select two distinct evidence items for comparison.");
      return;
    }

    setIsComparing(true);
    setComparisonError(null);
    try {
      const res = await api.compareImages({
        primary_evidence_id: primaryId,
        comparison_evidence_id: comparisonId,
        align_images: alignImages,
        difference_threshold: diffThreshold,
      });
      setComparisonResult(res);
      setViewMode("split_wipe");
      setSuccessNotice(`Comparison complete: ${res.difference_pixel_count.toLocaleString()} delta pixels (${res.difference_percentage.toFixed(2)}%) detected.`);
      setTimeout(() => setSuccessNotice(null), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Image comparison failed";
      setComparisonError(msg);
      setErrorNotice(msg);
    } finally {
      setIsComparing(false);
    }
  };

  // Handoff Comparison Centroid Patches to Quantum Lab
  const handleSendComparisonToQuantumLab = () => {
    if (!comparisonResult?.suggested_quantum_patch_a || !comparisonResult?.suggested_quantum_patch_b) {
      setErrorNotice("No quantized patches available from comparison centroid.");
      return;
    }
    sessionStorage.setItem("qtrace_handoff_patch_a", JSON.stringify(comparisonResult.suggested_quantum_patch_a));
    sessionStorage.setItem("qtrace_handoff_patch_b", JSON.stringify(comparisonResult.suggested_quantum_patch_b));
    sessionStorage.setItem("qtrace_handoff_patch", JSON.stringify(comparisonResult.suggested_quantum_patch_a));
    navigate("/quantum-lab");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-dark-950 text-slate-100 overflow-hidden select-none">
      {/* TOP WORKSTATION CONTROL HEADER */}
      <div className="h-14 px-4 bg-dark-900 border-b border-dark-800 flex items-center justify-between shrink-0 gap-4">
        {/* Left: Evidence Selectors */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-slate-200">Canvas</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-slate-400 uppercase">Primary:</span>
            <select
              value={primaryId}
              onChange={(e) => setPrimaryId(e.target.value)}
              className="bg-dark-950 border border-dark-750 text-xs text-slate-200 rounded px-2.5 py-1 max-w-[200px] truncate focus:outline-none focus:border-cyan-500"
            >
              {evidenceList.map((ev) => (
                <option key={ev.id} value={ev.id}>
                  {ev.original_filename} ({ev.file_size ? `${Math.round(ev.file_size / 1024)} KB` : ""})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-slate-400 uppercase">Compare:</span>
            <select
              value={comparisonId}
              onChange={(e) => setComparisonId(e.target.value)}
              className="bg-dark-950 border border-dark-750 text-xs text-slate-200 rounded px-2.5 py-1 max-w-[200px] truncate focus:outline-none focus:border-cyan-500"
            >
              <option value="">-- None (Single View) --</option>
              {evidenceList
                .filter((ev) => ev.id !== primaryId)
                .map((ev) => (
                  <option key={ev.id} value={ev.id}>
                    {ev.original_filename}
                  </option>
                ))}
            </select>
          </div>
        </div>

        {/* Center: Tool Mode Buttons */}
        <div className="flex items-center gap-1 bg-dark-950 p-1 rounded-lg border border-dark-800">
          <button
            type="button"
            onClick={() => setToolMode("pan")}
            title="Pan Viewport (Drag)"
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              toolMode === "pan"
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-dark-800"
            }`}
          >
            <Move className="w-3.5 h-3.5" />
            <span>Pan</span>
          </button>

          <button
            type="button"
            onClick={() => setToolMode("inspect")}
            title="Inspect Coordinates & Pixel Data"
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              toolMode === "inspect"
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-dark-800"
            }`}
          >
            <Crosshair className="w-3.5 h-3.5" />
            <span>Inspect</span>
          </button>

          <button
            type="button"
            onClick={() => setToolMode("roi_draw")}
            title="Draw New Region of Interest"
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              toolMode === "roi_draw"
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-dark-800"
            }`}
          >
            <Square className="w-3.5 h-3.5" />
            <span>Draw ROI</span>
          </button>

          <button
            type="button"
            onClick={() => setToolMode("roi_select")}
            title="Select & Resize Existing ROIs"
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              toolMode === "roi_select"
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-dark-800"
            }`}
          >
            <MousePointer className="w-3.5 h-3.5" />
            <span>Select ROI</span>
          </button>
        </div>

        {/* Center-Right: View Mode & Comparison Controls */}
        <div className="flex items-center gap-2">
          {comparisonId && (
            <div className="flex items-center gap-1 bg-dark-950 p-1 rounded-lg border border-dark-800">
              <button
                type="button"
                onClick={() => setViewMode("single")}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  viewMode === "single"
                    ? "bg-cyan-500/20 text-cyan-400"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                title="Single Primary Image"
              >
                Single
              </button>
              <button
                type="button"
                onClick={() => setViewMode("split_wipe")}
                className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                  viewMode === "split_wipe"
                    ? "bg-cyan-500/20 text-cyan-400"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                title="Split Wipe Comparison"
              >
                <SplitSquareVertical className="w-3.5 h-3.5" />
                <span>Split-Wipe</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("overlay")}
                className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                  viewMode === "overlay"
                    ? "bg-cyan-500/20 text-cyan-400"
                    : "text-slate-400 hover:text-slate-200"
                }`}
                title="Opacity Blend Overlay"
              >
                <Blend className="w-3.5 h-3.5" />
                <span>Overlay</span>
              </button>
              {comparisonResult && (
                <button
                  type="button"
                  onClick={() => setViewMode("difference")}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                    viewMode === "difference"
                      ? "bg-cyan-500/20 text-cyan-400"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                  title="Heatmap Difference View"
                >
                  <FileDiff className="w-3.5 h-3.5" />
                  <span>Difference</span>
                </button>
              )}
            </div>
          )}

          {/* Quick Actions: Toggle Overlays */}
          <button
            type="button"
            onClick={() => setShowAnnotations(!showAnnotations)}
            title={showAnnotations ? "Hide ROI Overlays" : "Show ROI Overlays"}
            className={`p-1.5 rounded border text-xs transition-colors ${
              showAnnotations
                ? "bg-dark-800 text-cyan-400 border-dark-700"
                : "bg-dark-950 text-slate-500 border-dark-800"
            }`}
          >
            {showAnnotations ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* SUB-TOOLBAR (Sliders for Split Wipe & Overlay / Difference) */}
      {(viewMode === "split_wipe" || viewMode === "overlay" || viewMode === "difference") && (
        <div className="h-9 px-6 bg-dark-900/90 border-b border-dark-800 flex items-center justify-between text-xs text-slate-300">
          {viewMode === "split_wipe" && (
            <div className="flex items-center gap-3 w-full max-w-md">
              <span className="font-mono text-[11px] text-cyan-400">Swipe Split Position:</span>
              <input
                type="range"
                min="0"
                max="100"
                value={splitPosition}
                onChange={(e) => setSplitPosition(parseInt(e.target.value, 10))}
                className="w-full accent-cyan-400 h-1.5 bg-dark-800 rounded-lg cursor-pointer"
              />
              <span className="font-mono text-xs text-slate-300 min-w-[40px]">
                {splitPosition}%
              </span>
            </div>
          )}

          {(viewMode === "overlay" || viewMode === "difference") && (
            <div className="flex items-center gap-3 w-full max-w-md">
              <span className="font-mono text-[11px] text-cyan-400">
                {viewMode === "difference" ? "Heatmap Opacity:" : "Overlay Blend Opacity:"}
              </span>
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(overlayOpacity * 100)}
                onChange={(e) => setOverlayOpacity(parseInt(e.target.value, 10) / 100)}
                className="w-full accent-cyan-400 h-1.5 bg-dark-800 rounded-lg cursor-pointer"
              />
              <span className="font-mono text-xs text-slate-300 min-w-[40px]">
                {Math.round(overlayOpacity * 100)}%
              </span>
            </div>
          )}

          {comparisonId && (
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={alignImages}
                  onChange={(e) => setAlignImages(e.target.checked)}
                  className="rounded bg-dark-950 border-dark-700 text-cyan-500 focus:ring-0"
                />
                <span>SIFT Homography Alignment</span>
              </label>

              <Button
                variant="outline"
                size="sm"
                onClick={handleRunComparison}
                disabled={isComparing}
                className="h-6 text-xs px-2.5 border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10"
              >
                {isComparing ? (
                  <>
                    <LoadingSpinner size="sm" className="w-3 h-3 mr-1" />
                    <span>Comparing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3 h-3 mr-1 text-cyan-400" />
                    <span>Recompute Delta</span>
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      )}

      {/* MAIN WORKSPACE BODY */}
      <div className="flex-1 flex overflow-hidden">
        {/* CENTER FORENSIC CANVAS */}
        <div className="flex-1 relative bg-dark-950 overflow-hidden">
          {isLoadingEvidence ? (
            <div className="h-full flex flex-col items-center justify-center gap-3 text-slate-400">
              <LoadingSpinner size="lg" />
              <p className="text-sm font-mono">Loading evidence files...</p>
            </div>
          ) : !primarySrc ? (
            <div className="h-full flex flex-col items-center justify-center gap-2 text-slate-500">
              <AlertTriangle className="w-8 h-8 text-amber-500/60" />
              <p className="text-sm">No evidence selected. Please select an evidence item to inspect.</p>
            </div>
          ) : (
            <ForensicCanvas
              primarySrc={primarySrc}
              primaryFilename={primaryEvidence?.original_filename}
              comparisonSrc={comparisonSrc}
              comparisonFilename={comparisonEvidence?.original_filename}
              diffArtifactSrc={diffArtifactSrc}
              rois={rois}
              candidateRegions={candidateRegions}
              selectedRoiId={selectedRoi?.id}
              toolMode={toolMode}
              viewMode={viewMode}
              splitPosition={splitPosition}
              overlayOpacity={overlayOpacity}
              showAnnotations={showAnnotations}
              showCandidates={showCandidates}
              onSelectRoi={(roi) => setSelectedRoi(roi)}
              onCreateRoi={handleCreateRoi}
              onUpdateRoiCoords={handleUpdateRoiCoords}
              onPixelHover={(sample) => setHoverPixel(sample)}
              onZoomChange={(z) => setCurrentZoom(z)}
            />
          )}

          {/* Toast / Notification Banners */}
          {errorNotice && (
            <div className="absolute top-4 right-4 z-40 max-w-md p-3 bg-red-950/90 border border-red-800 text-red-200 text-xs rounded-lg shadow-xl flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div className="flex-1">{errorNotice}</div>
              <button
                type="button"
                onClick={() => setErrorNotice(null)}
                className="text-red-400 hover:text-red-100 ml-2 font-bold"
              >
                ×
              </button>
            </div>
          )}

          {successNotice && (
            <div className="absolute top-4 right-4 z-40 max-w-md p-3 bg-cyan-950/90 border border-cyan-800 text-cyan-200 text-xs rounded-lg shadow-xl flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
              <div className="flex-1">{successNotice}</div>
              <button
                type="button"
                onClick={() => setSuccessNotice(null)}
                className="text-cyan-400 hover:text-cyan-100 ml-2 font-bold"
              >
                ×
              </button>
            </div>
          )}
        </div>

        {/* RIGHT SIDEBAR INSPECTOR & ROI MANAGER */}
        <div className="w-80 bg-dark-900 border-l border-dark-800 flex flex-col shrink-0 overflow-y-auto">
          {/* Header */}
          <div className="p-3 border-b border-dark-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Square className="w-4 h-4 text-cyan-400" />
              <span className="font-semibold text-xs tracking-wider uppercase text-slate-200">
                Region Inspector
              </span>
            </div>
            <span className="text-[11px] font-mono text-cyan-400">
              {rois.length} {rois.length === 1 ? "ROI" : "ROIs"}
            </span>
          </div>

          {/* ACTIVE ROI DETAILS / EDITING */}
          {selectedRoi ? (
            <div className="p-4 space-y-4 border-b border-dark-800">
              <div>
                <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                  Region Label
                </label>
                <input
                  type="text"
                  value={editLabel}
                  onChange={(e) => setEditLabel(e.target.value)}
                  className="w-full bg-dark-950 border border-dark-750 rounded px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Geometry Coordinates (Read-only Original Image Coordinates) */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-dark-950 p-2.5 rounded border border-dark-800">
                <div>
                  <span className="text-slate-500 block text-[10px]">ORIGIN (X, Y)</span>
                  <span className="text-slate-200 font-semibold">
                    {selectedRoi.x}, {selectedRoi.y}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">SIZE (W × H)</span>
                  <span className="text-slate-200 font-semibold">
                    {selectedRoi.width} × {selectedRoi.height} px
                  </span>
                </div>
              </div>

              {/* Color Swatch & Confidence Slider */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                    Color Accent
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editColor}
                      onChange={(e) => setEditColor(e.target.value)}
                      className="w-7 h-7 rounded border border-dark-700 bg-dark-950 cursor-pointer p-0"
                    />
                    <span className="text-[11px] font-mono text-slate-400">{editColor}</span>
                  </div>
                </div>

                <div>
                  <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                    Confidence ({Math.round(editConfidence * 100)}%)
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={Math.round(editConfidence * 100)}
                    onChange={(e) => setEditConfidence(parseInt(e.target.value, 10) / 100)}
                    className="w-full accent-cyan-400 h-1.5 bg-dark-800 rounded cursor-pointer mt-2"
                  />
                </div>
              </div>

              {/* Factual Observation */}
              <div>
                <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                  Factual Observation
                </label>
                <textarea
                  rows={2}
                  value={editObservation}
                  onChange={(e) => setEditObservation(e.target.value)}
                  placeholder="Technical facts (e.g. sharp high-frequency edge transition)..."
                  className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                />
              </div>

              {/* Investigative Hypothesis */}
              <div>
                <label className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                  Investigative Hypothesis
                </label>
                <textarea
                  rows={2}
                  value={editHypothesis}
                  onChange={(e) => setEditHypothesis(e.target.value)}
                  placeholder="Investigative hypothesis (e.g. possible copy-move splice artifact)..."
                  className="w-full bg-dark-950 border border-dark-750 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 resize-none"
                />
              </div>

              {/* Save & Delete Action Row */}
              <div className="flex items-center gap-2 pt-1">
                <Button
                  size="sm"
                  onClick={handleSaveRoi}
                  disabled={isSavingRoi}
                  className="flex-1 text-xs"
                >
                  <Save className="w-3.5 h-3.5 mr-1" />
                  <span>Save ROI</span>
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteRoi(selectedRoi.id)}
                  className="text-xs text-red-400 hover:text-red-300 hover:bg-red-950/30 border-red-900/50"
                  title="Delete Region"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </Button>
              </div>

              {/* Sub-Region Crop Extraction Button */}
              <div className="pt-2 border-t border-dark-800">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCropRoi}
                  disabled={isCropping}
                  className="w-full text-xs border-dark-750 text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40"
                >
                  <Crop className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                  <span>{isCropping ? "Extracting Sub-Region..." : "Extract Sub-Region Crop"}</span>
                </Button>

                {/* Crop Result Card */}
                {lastCropArtifact && (
                  <div className="mt-3 p-2.5 rounded bg-dark-950 border border-dark-800 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono text-cyan-400 uppercase">
                        Crop Artifact Created
                      </span>
                      <span className="text-[9px] font-mono text-slate-400">
                        {lastCropArtifact.crop_width}×{lastCropArtifact.crop_height}
                      </span>
                    </div>

                    <div className="w-full h-24 bg-dark-900 rounded overflow-hidden flex items-center justify-center border border-dark-800">
                      <img
                        src={api.getDerivativeFileUrl(lastCropArtifact.artifact_id)}
                        alt="Crop Preview"
                        className="max-h-full max-w-full object-contain"
                      />
                    </div>

                    <div className="text-[10px] font-mono text-slate-400 truncate">
                      SHA: {lastCropArtifact.sha256_hash.substring(0, 20)}...
                    </div>

                    {lastCropArtifact.suggested_quantum_patch && (
                      <Button
                        size="sm"
                        onClick={handleSendRoiToQuantumLab}
                        className="w-full text-xs bg-cyan-600/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-600/30"
                      >
                        <Cpu className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                        <span>Send 4×4 Patch to Quantum Lab</span>
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-slate-500 text-xs border-b border-dark-800">
              <MousePointer className="w-6 h-6 mx-auto mb-2 text-slate-600" />
              <p>No region selected.</p>
              <p className="text-[11px] text-slate-600 mt-1">
                Select a tool above or draw a rectangle on the canvas to inspect an anomaly.
              </p>
            </div>
          )}

          {/* ALL SAVED REGIONS LIST */}
          <div className="p-3 flex-1">
            <span className="text-[10px] font-mono uppercase text-slate-500 block mb-2">
              Saved ROIs in this Evidence
            </span>

            {rois.length === 0 ? (
              <div className="text-center py-6 text-slate-600 text-xs">
                No regions recorded yet.
              </div>
            ) : (
              <div className="space-y-1.5">
                {rois.map((roi) => (
                  <div
                    key={roi.id}
                    onClick={() => {
                      setSelectedRoi(roi);
                      setToolMode("roi_select");
                    }}
                    className={`p-2 rounded border cursor-pointer transition-colors text-xs flex items-center justify-between ${
                      selectedRoi?.id === roi.id
                        ? "bg-dark-800 border-cyan-500/50 text-slate-100"
                        : "bg-dark-950/60 border-dark-800 text-slate-400 hover:border-dark-700 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <div
                        className="w-2.5 h-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: roi.color || "#00F2FE" }}
                      />
                      <span className="font-medium truncate">{roi.roi_label}</span>
                    </div>

                    <div className="flex items-center gap-1 text-[10px] font-mono text-slate-500 shrink-0">
                      <span>{roi.width}×{roi.height}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* COMPARISON METRICS SUMMARY CARD (if comparison active) */}
          {comparisonResult && (
            <div className="p-4 border-t border-dark-800 bg-dark-950/90 text-xs space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] uppercase text-cyan-400 font-semibold">
                  Alignment & Delta Metrics
                </span>
                <Badge variant={comparisonResult.difference_percentage > 5 ? "warning" : "verified"}>
                  {comparisonResult.alignment_status}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-2 font-mono text-[11px] bg-dark-900 p-2 rounded border border-dark-800">
                <div>
                  <span className="text-slate-500 block text-[9px]">DELTA PIXELS</span>
                  <span className="text-slate-200 font-semibold">
                    {comparisonResult.difference_pixel_count.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">DELTA RATIO</span>
                  <span className="text-cyan-400 font-semibold">
                    {comparisonResult.difference_percentage.toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">MAE / RMSE</span>
                  <span className="text-slate-200">
                    {comparisonResult.mean_absolute_error.toFixed(1)} / {comparisonResult.root_mean_square_error.toFixed(1)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">PSNR / SSIM</span>
                  <span className="text-slate-200">
                    {comparisonResult.psnr_db.toFixed(1)} dB / {comparisonResult.ssim_score.toFixed(3)}
                  </span>
                </div>
              </div>

              {/* Quantum Lab Comparison Handoff */}
              {comparisonResult.suggested_quantum_patch_a && comparisonResult.suggested_quantum_patch_b && (
                <Button
                  size="sm"
                  onClick={handleSendComparisonToQuantumLab}
                  className="w-full text-xs bg-cyan-600/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-600/30"
                >
                  <Cpu className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                  <span>Send Centroid Delta to Quantum Lab</span>
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* BOTTOM STATUS BAR (Exact Pixel Coordinates & Integrity Readout) */}
      <div className="h-7 px-4 bg-dark-900 border-t border-dark-800 flex items-center justify-between text-[11px] font-mono text-slate-400 shrink-0">
        <div className="flex items-center gap-4">
          {hoverPixel ? (
            <>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-500">CURSOR:</span>
                <span className="text-cyan-400 font-semibold">
                  X: {hoverPixel.x} px, Y: {hoverPixel.y} px
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-500">COLOR:</span>
                <div
                  className="w-3 h-3 rounded-sm border border-dark-700"
                  style={{
                    backgroundColor: `rgb(${hoverPixel.r}, ${hoverPixel.g}, ${hoverPixel.b})`,
                  }}
                />
                <span className="text-slate-300">
                  RGB({hoverPixel.r}, {hoverPixel.g}, {hoverPixel.b})
                </span>
                <span className="text-slate-500 text-[10px]">
                  (Luma: {hoverPixel.luminance})
                </span>
              </div>
            </>
          ) : (
            <span className="text-slate-500">Hover canvas to inspect pixel values</span>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-500">TOOL:</span>
            <span className="text-slate-300 uppercase">{toolMode}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-500">ZOOM:</span>
            <span className="text-cyan-400 font-semibold">{Math.round(currentZoom * 100)}%</span>
          </div>

          <div className="flex items-center gap-1.5 text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="text-[10px]">WORM INTEGRITY LOCKED</span>
          </div>
        </div>
      </div>
    </div>
  );
};
