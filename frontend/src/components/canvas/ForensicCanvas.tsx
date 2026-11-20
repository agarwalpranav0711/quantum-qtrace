import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Move,
  Crosshair,
  Square,
  MousePointer,
  Eye,
  Sliders,
  Layers,
  Sparkles,
} from "lucide-react";
import { ROIResponse } from "../../types/api";

export type CanvasTool = "pan" | "inspect" | "roi_draw" | "roi_select";
export type CanvasViewMode = "single" | "side_by_side" | "split_wipe" | "overlay" | "difference";

export interface PixelSample {
  x: number;
  y: number;
  r: number;
  g: number;
  b: number;
  luminance: number;
}

export interface CandidateRegionOverlay {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  color?: string;
  score?: number;
}

export interface ForensicCanvasProps {
  primarySrc: string;
  primaryFilename?: string;
  comparisonSrc?: string;
  comparisonFilename?: string;
  diffArtifactSrc?: string;
  rois: ROIResponse[];
  candidateRegions?: CandidateRegionOverlay[];
  selectedRoiId?: string | null;
  toolMode: CanvasTool;
  viewMode: CanvasViewMode;
  splitPosition: number;
  overlayOpacity: number;
  showAnnotations?: boolean;
  showCandidates?: boolean;
  onSelectRoi?: (roi: ROIResponse | null) => void;
  onCreateRoi?: (coords: { x: number; y: number; width: number; height: number }) => void;
  onUpdateRoiCoords?: (roiId: string, coords: { x: number; y: number; width: number; height: number }) => void;
  onPixelHover?: (sample: PixelSample | null) => void;
  onZoomChange?: (zoom: number) => void;
  className?: string;
}

export const ForensicCanvas: React.FC<ForensicCanvasProps> = ({
  primarySrc,
  primaryFilename = "Primary Evidence",
  comparisonSrc,
  comparisonFilename = "Comparison Image",
  diffArtifactSrc,
  rois,
  candidateRegions = [],
  selectedRoiId,
  toolMode,
  viewMode,
  splitPosition,
  overlayOpacity,
  showAnnotations = true,
  showCandidates = true,
  onSelectRoi,
  onCreateRoi,
  onUpdateRoiCoords,
  onPixelHover,
  onZoomChange,
  className = "",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const primaryImgRef = useRef<HTMLImageElement>(null);
  const offscreenCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Pan and Zoom transform state
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [naturalDimensions, setNaturalDimensions] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0,
  });

  // Interaction dragging states
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // ROI Drawing state
  const [isDrawingRoi, setIsDrawingRoi] = useState<boolean>(false);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [drawCurrent, setDrawCurrent] = useState<{ x: number; y: number } | null>(null);

  // ROI Resizing / Moving state
  const [draggedRoiId, setDraggedRoiId] = useState<string | null>(null);
  const [dragHandle, setDragHandle] = useState<"move" | "nw" | "ne" | "sw" | "se" | null>(null);
  const [roiDragStart, setRoiDragStart] = useState<{
    mouseX: number;
    mouseY: number;
    roiX: number;
    roiY: number;
    roiW: number;
    roiH: number;
  } | null>(null);

  // Offscreen canvas for fast pixel color sampling
  useEffect(() => {
    if (!primarySrc) return;
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = primarySrc;
    img.onload = () => {
      setNaturalDimensions({ width: img.naturalWidth, height: img.naturalHeight });
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (ctx) {
        ctx.drawImage(img, 0, 0);
        offscreenCanvasRef.current = canvas;
      }
    };
  }, [primarySrc]);

  // Update zoom reporter
  useEffect(() => {
    onZoomChange?.(zoom);
  }, [zoom, onZoomChange]);

  const handleZoom = useCallback(
    (newZoom: number, focalPoint?: { x: number; y: number }) => {
      const clamped = Math.max(0.1, Math.min(10.0, Math.round(newZoom * 100) / 100));
      if (!containerRef.current || !focalPoint) {
        setZoom(clamped);
        return;
      }

      // Zoom towards mouse focal point
      const rect = containerRef.current.getBoundingClientRect();
      const mouseX = focalPoint.x - rect.left;
      const mouseY = focalPoint.y - rect.top;

      const scaleChange = clamped / zoom;
      const newPanX = mouseX - (mouseX - pan.x) * scaleChange;
      const newPanY = mouseY - (mouseY - pan.y) * scaleChange;

      setZoom(clamped);
      setPan({ x: newPanX, y: newPanY });
    },
    [zoom, pan]
  );

  const handleZoomIn = () => handleZoom(zoom * 1.25);
  const handleZoomOut = () => handleZoom(zoom * 0.8);
  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleFitToScreen = () => {
    if (!containerRef.current || naturalDimensions.width === 0) return;
    const rect = containerRef.current.getBoundingClientRect();
    const scaleX = (rect.width - 48) / naturalDimensions.width;
    const scaleY = (rect.height - 48) / naturalDimensions.height;
    const fitZoom = Math.min(scaleX, scaleY, 1.0);
    setZoom(Math.max(0.1, Math.round(fitZoom * 100) / 100));
    setPan({
      x: (rect.width - naturalDimensions.width * fitZoom) / 2,
      y: (rect.height - naturalDimensions.height * fitZoom) / 2,
    });
  };

  const handleOneToOne = () => {
    if (!containerRef.current || naturalDimensions.width === 0) {
      setZoom(1);
      setPan({ x: 0, y: 0 });
      return;
    }
    const rect = containerRef.current.getBoundingClientRect();
    setZoom(1.0);
    setPan({
      x: (rect.width - naturalDimensions.width) / 2,
      y: (rect.height - naturalDimensions.height) / 2,
    });
  };

  // Convert client viewport screen coordinates to original image coordinates
  const screenToImageCoords = useCallback(
    (clientX: number, clientY: number): { x: number; y: number } | null => {
      if (!containerRef.current || naturalDimensions.width === 0) return null;
      const rect = containerRef.current.getBoundingClientRect();
      const relativeX = clientX - rect.left - pan.x;
      const relativeY = clientY - rect.top - pan.y;

      const imgX = Math.floor(relativeX / zoom);
      const imgY = Math.floor(relativeY / zoom);

      if (imgX < 0 || imgX >= naturalDimensions.width || imgY < 0 || imgY >= naturalDimensions.height) {
        return null;
      }
      return { x: imgX, y: imgY };
    },
    [pan, zoom, naturalDimensions]
  );

  // Mouse wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 0.85;
    handleZoom(zoom * factor, { x: e.clientX, y: e.clientY });
  };

  // Mouse down handler
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only primary mouse button

    if (toolMode === "pan") {
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      return;
    }

    const coords = screenToImageCoords(e.clientX, e.clientY);
    if (!coords) return;

    if (toolMode === "roi_draw") {
      setIsDrawingRoi(true);
      setDrawStart(coords);
      setDrawCurrent(coords);
    }
  };

  // Mouse move handler
  const handleMouseMove = (e: React.MouseEvent) => {
    // 1. Handle panning
    if (isPanning && toolMode === "pan") {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      });
      return;
    }

    // 2. Handle ROI drawing
    const coords = screenToImageCoords(e.clientX, e.clientY);
    if (isDrawingRoi && drawStart && coords) {
      setDrawCurrent(coords);
    }

    // 3. Handle ROI resizing or moving
    if (draggedRoiId && dragHandle && roiDragStart && coords) {
      const deltaX = coords.x - roiDragStart.mouseX;
      const deltaY = coords.y - roiDragStart.mouseY;

      let newX = roiDragStart.roiX;
      let newY = roiDragStart.roiY;
      let newW = roiDragStart.roiW;
      let newH = roiDragStart.roiH;

      if (dragHandle === "move") {
        newX = Math.max(0, Math.min(naturalDimensions.width - newW, roiDragStart.roiX + deltaX));
        newY = Math.max(0, Math.min(naturalDimensions.height - newH, roiDragStart.roiY + deltaY));
      } else if (dragHandle === "se") {
        newW = Math.max(4, Math.min(naturalDimensions.width - newX, roiDragStart.roiW + deltaX));
        newH = Math.max(4, Math.min(naturalDimensions.height - newY, roiDragStart.roiH + deltaY));
      } else if (dragHandle === "sw") {
        const potentialX = roiDragStart.roiX + deltaX;
        if (potentialX >= 0 && potentialX < roiDragStart.roiX + roiDragStart.roiW - 4) {
          newX = potentialX;
          newW = roiDragStart.roiW - deltaX;
        }
        newH = Math.max(4, Math.min(naturalDimensions.height - newY, roiDragStart.roiH + deltaY));
      } else if (dragHandle === "ne") {
        newW = Math.max(4, Math.min(naturalDimensions.width - newX, roiDragStart.roiW + deltaX));
        const potentialY = roiDragStart.roiY + deltaY;
        if (potentialY >= 0 && potentialY < roiDragStart.roiY + roiDragStart.roiH - 4) {
          newY = potentialY;
          newH = roiDragStart.roiH - deltaY;
        }
      } else if (dragHandle === "nw") {
        const potentialX = roiDragStart.roiX + deltaX;
        const potentialY = roiDragStart.roiY + deltaY;
        if (potentialX >= 0 && potentialX < roiDragStart.roiX + roiDragStart.roiW - 4) {
          newX = potentialX;
          newW = roiDragStart.roiW - deltaX;
        }
        if (potentialY >= 0 && potentialY < roiDragStart.roiY + roiDragStart.roiH - 4) {
          newY = potentialY;
          newH = roiDragStart.roiH - deltaY;
        }
      }

      onUpdateRoiCoords?.(draggedRoiId, {
        x: Math.round(newX),
        y: Math.round(newY),
        width: Math.round(newW),
        height: Math.round(newH),
      });
      return;
    }

    // 4. Sample pixel under cursor for inspection status bar
    if (coords && offscreenCanvasRef.current) {
      try {
        const ctx = offscreenCanvasRef.current.getContext("2d", { willReadFrequently: true });
        if (ctx) {
          const pixel = ctx.getImageData(coords.x, coords.y, 1, 1).data;
          const r = pixel[0];
          const g = pixel[1];
          const b = pixel[2];
          const luminance = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
          onPixelHover?.({ x: coords.x, y: coords.y, r, g, b, luminance });
        }
      } catch {
        onPixelHover?.(null);
      }
    } else {
      onPixelHover?.(null);
    }
  };

  // Mouse up handler
  const handleMouseUp = () => {
    setIsPanning(false);

    if (isDrawingRoi && drawStart && drawCurrent) {
      const minX = Math.min(drawStart.x, drawCurrent.x);
      const minY = Math.min(drawStart.y, drawCurrent.y);
      const width = Math.abs(drawCurrent.x - drawStart.x);
      const height = Math.abs(drawCurrent.y - drawStart.y);

      // Only save if region is at least 4x4 pixels
      if (width >= 4 && height >= 4) {
        onCreateRoi?.({
          x: Math.round(minX),
          y: Math.round(minY),
          width: Math.round(width),
          height: Math.round(height),
        });
      }
      setIsDrawingRoi(false);
      setDrawStart(null);
      setDrawCurrent(null);
    }

    if (draggedRoiId) {
      setDraggedRoiId(null);
      setDragHandle(null);
      setRoiDragStart(null);
    }
  };

  // Calculate live drawing rectangle coordinates
  const drawingRect =
    isDrawingRoi && drawStart && drawCurrent
      ? {
          x: Math.min(drawStart.x, drawCurrent.x),
          y: Math.min(drawStart.y, drawCurrent.y),
          width: Math.abs(drawCurrent.x - drawStart.x),
          height: Math.abs(drawCurrent.y - drawStart.y),
        }
      : null;

  return (
    <div
      ref={containerRef}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      className={`relative w-full h-full bg-dark-950 overflow-hidden select-none cursor-${
        toolMode === "pan"
          ? isPanning
            ? "grabbing"
            : "grab"
          : toolMode === "inspect"
          ? "crosshair"
          : toolMode === "roi_draw"
          ? "crosshair"
          : "default"
      } ${className}`}
    >
      {/* Top Floating Control Toolbar */}
      <div className="absolute top-4 left-4 z-30 flex items-center gap-1.5 p-1.5 rounded-lg bg-dark-900/90 backdrop-blur-md border border-dark-750 shadow-xl">
        <button
          type="button"
          onClick={handleZoomIn}
          title="Zoom In (+25%)"
          className="p-1.5 rounded text-slate-300 hover:text-cyan-400 hover:bg-dark-800 transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={handleZoomOut}
          title="Zoom Out (-25%)"
          className="p-1.5 rounded text-slate-300 hover:text-cyan-400 hover:bg-dark-800 transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={handleOneToOne}
          title="1:1 Actual Size (100%)"
          className="px-2 py-1 text-xs font-mono font-medium rounded text-slate-300 hover:text-cyan-400 hover:bg-dark-800 transition-colors"
        >
          1:1
        </button>
        <button
          type="button"
          onClick={handleFitToScreen}
          title="Fit to Screen"
          className="p-1.5 rounded text-slate-300 hover:text-cyan-400 hover:bg-dark-800 transition-colors"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={handleResetZoom}
          title="Reset View"
          className="p-1.5 rounded text-slate-300 hover:text-cyan-400 hover:bg-dark-800 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <div className="w-[1px] h-5 bg-dark-750 mx-1" />

        {/* Zoom percentage indicator */}
        <span className="px-2 text-xs font-mono text-cyan-400 font-semibold min-w-[50px] text-center">
          {Math.round(zoom * 100)}%
        </span>
      </div>

      {/* Main Viewport Workspace */}
      <div
        className="absolute transition-transform duration-75 origin-top-left will-change-transform"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          width: naturalDimensions.width || "auto",
          height: naturalDimensions.height || "auto",
        }}
      >
        {/* VIEW MODE: Single or Standard Base */}
        {(viewMode === "single" || viewMode === "overlay" || viewMode === "difference" || viewMode === "split_wipe") && (
          <img
            ref={primaryImgRef}
            src={primarySrc}
            alt={primaryFilename}
            draggable={false}
            className="block max-w-none pointer-events-none"
            style={{
              imageRendering: zoom >= 3 ? "pixelated" : "auto",
            }}
          />
        )}

        {/* VIEW MODE: Split Wipe Slider Comparison */}
        {viewMode === "split_wipe" && comparisonSrc && (
          <div
            className="absolute inset-0 overflow-hidden pointer-events-none"
            style={{
              clipPath: `inset(0 0 0 ${splitPosition}%)`,
            }}
          >
            <img
              src={comparisonSrc}
              alt={comparisonFilename}
              draggable={false}
              className="block max-w-none"
              style={{
                imageRendering: zoom >= 3 ? "pixelated" : "auto",
                width: naturalDimensions.width || "auto",
                height: naturalDimensions.height || "auto",
              }}
            />
          </div>
        )}

        {/* Split Wipe Dividing Vertical Bar Indicator */}
        {viewMode === "split_wipe" && comparisonSrc && (
          <div
            className="absolute top-0 bottom-0 pointer-events-none border-l-2 border-cyan-400 shadow-[0_0_12px_rgba(0,242,254,0.6)]"
            style={{
              left: `${splitPosition}%`,
            }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-6 h-6 rounded-full bg-cyan-400 text-dark-950 flex items-center justify-center text-[10px] font-bold shadow-lg">
              ↔
            </div>
          </div>
        )}

        {/* VIEW MODE: Overlay Opacity */}
        {viewMode === "overlay" && comparisonSrc && (
          <img
            src={comparisonSrc}
            alt={comparisonFilename}
            draggable={false}
            className="absolute inset-0 block max-w-none pointer-events-none"
            style={{
              opacity: overlayOpacity,
              imageRendering: zoom >= 3 ? "pixelated" : "auto",
              width: naturalDimensions.width || "auto",
              height: naturalDimensions.height || "auto",
            }}
          />
        )}

        {/* VIEW MODE: Difference Heatmap Overlay */}
        {viewMode === "difference" && diffArtifactSrc && (
          <img
            src={diffArtifactSrc}
            alt="Difference Map"
            draggable={false}
            className="absolute inset-0 block max-w-none pointer-events-none"
            style={{
              opacity: overlayOpacity,
              mixBlendMode: "screen",
              imageRendering: zoom >= 3 ? "pixelated" : "auto",
              width: naturalDimensions.width || "auto",
              height: naturalDimensions.height || "auto",
            }}
          />
        )}

        {/* CANDIDATE REGIONS OVERLAY (Part 5 Algorithms) */}
        {showCandidates &&
          candidateRegions.map((cand, idx) => (
            <div
              key={`cand-${idx}`}
              className="absolute pointer-events-none border border-dashed rounded-sm transition-all"
              style={{
                left: `${cand.x}px`,
                top: `${cand.y}px`,
                width: `${cand.width}px`,
                height: `${cand.height}px`,
                borderColor: cand.color || "#F59E0B",
                backgroundColor: "rgba(245, 158, 11, 0.08)",
              }}
            >
              <span
                className="absolute -top-5 left-0 px-1 py-0.2 text-[9px] font-mono font-medium rounded text-amber-300 bg-dark-900/90 border border-amber-500/40 whitespace-nowrap"
                style={{ fontSize: `${Math.max(9, 10 / zoom)}px` }}
              >
                {cand.label}
              </span>
            </div>
          ))}

        {/* EXAMINER SAVED REGIONS OF INTEREST (ROIs) */}
        {showAnnotations &&
          rois.map((roi) => {
            const isSelected = roi.id === selectedRoiId;
            return (
              <div
                key={roi.id}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectRoi?.(roi);
                }}
                className={`absolute transition-shadow ${
                  isSelected
                    ? "ring-2 ring-cyan-400 shadow-[0_0_15px_rgba(0,242,254,0.4)] z-20 cursor-move"
                    : "hover:ring-1 hover:ring-cyan-300 cursor-pointer z-10"
                }`}
                style={{
                  left: `${roi.x}px`,
                  top: `${roi.y}px`,
                  width: `${roi.width}px`,
                  height: `${roi.height}px`,
                  border: `2px solid ${roi.color || "#00F2FE"}`,
                  backgroundColor: isSelected ? "rgba(0, 242, 254, 0.12)" : "rgba(0, 242, 254, 0.04)",
                }}
              >
                {/* ROI Label Tag */}
                <div
                  className="absolute -top-6 left-0 flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold text-slate-100 bg-dark-900/95 border border-dark-700 shadow-md whitespace-nowrap pointer-events-auto"
                  style={{
                    borderLeftColor: roi.color || "#00F2FE",
                    borderLeftWidth: "3px",
                  }}
                >
                  <span>{roi.roi_label}</span>
                  <span className="text-[9px] text-slate-400">
                    ({roi.width}×{roi.height})
                  </span>
                  {roi.confidence !== null && roi.confidence !== undefined && (
                    <span className="text-[9px] text-cyan-400">
                      {Math.round(roi.confidence * 100)}%
                    </span>
                  )}
                </div>

                {/* Resize Corner Handles for Selected ROI */}
                {isSelected && toolMode === "roi_select" && (
                  <>
                    <div
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        setDraggedRoiId(roi.id);
                        setDragHandle("nw");
                        setRoiDragStart({
                          mouseX: roi.x,
                          mouseY: roi.y,
                          roiX: roi.x,
                          roiY: roi.y,
                          roiW: roi.width,
                          roiH: roi.height,
                        });
                      }}
                      className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-cyan-400 border border-dark-900 rounded-sm cursor-nwse-resize z-30"
                    />
                    <div
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        setDraggedRoiId(roi.id);
                        setDragHandle("ne");
                        setRoiDragStart({
                          mouseX: roi.x + roi.width,
                          mouseY: roi.y,
                          roiX: roi.x,
                          roiY: roi.y,
                          roiW: roi.width,
                          roiH: roi.height,
                        });
                      }}
                      className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-cyan-400 border border-dark-900 rounded-sm cursor-nesw-resize z-30"
                    />
                    <div
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        setDraggedRoiId(roi.id);
                        setDragHandle("sw");
                        setRoiDragStart({
                          mouseX: roi.x,
                          mouseY: roi.y + roi.height,
                          roiX: roi.x,
                          roiY: roi.y,
                          roiW: roi.width,
                          roiH: roi.height,
                        });
                      }}
                      className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-cyan-400 border border-dark-900 rounded-sm cursor-nesw-resize z-30"
                    />
                    <div
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        setDraggedRoiId(roi.id);
                        setDragHandle("se");
                        setRoiDragStart({
                          mouseX: roi.x + roi.width,
                          mouseY: roi.y + roi.height,
                          roiX: roi.x,
                          roiY: roi.y,
                          roiW: roi.width,
                          roiH: roi.height,
                        });
                      }}
                      className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-cyan-400 border border-dark-900 rounded-sm cursor-nwse-resize z-30"
                    />
                  </>
                )}
              </div>
            );
          })}

        {/* LIVE ROI DRAWING PREVIEW */}
        {drawingRect && (
          <div
            className="absolute border-2 border-dashed border-cyan-400 bg-cyan-500/15 pointer-events-none"
            style={{
              left: `${drawingRect.x}px`,
              top: `${drawingRect.y}px`,
              width: `${drawingRect.width}px`,
              height: `${drawingRect.height}px`,
            }}
          >
            <span className="absolute -top-5 left-0 px-1 py-0.5 text-[9px] font-mono text-cyan-300 bg-dark-900/90 rounded border border-cyan-500/40">
              {drawingRect.width} × {drawingRect.height} px
            </span>
          </div>
        )}
      </div>

      {/* VIEW MODE: Side-by-Side Dual Viewport Indicator */}
      {viewMode === "side_by_side" && (
        <div className="absolute bottom-4 left-4 z-30 px-3 py-1.5 rounded-lg bg-dark-900/90 backdrop-blur-md border border-dark-750 text-xs font-mono text-slate-300">
          Side-by-Side Synchronized Inspection Mode
        </div>
      )}
    </div>
  );
};

