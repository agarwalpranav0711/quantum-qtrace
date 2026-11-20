import React, { useState, useRef, useEffect } from "react";
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Crosshair, ShieldCheck, ShieldAlert } from "lucide-react";
import { Badge } from "../ui/Badge";

export interface ForensicImageViewerProps {
  src: string;
  alt: string;
  originalFilename: string;
  sha256?: string;
  isOriginal?: boolean;
  isVerified?: boolean;
  dimensions?: { width: number; height: number };
  className?: string;
}

export const ForensicImageViewer: React.FC<ForensicImageViewerProps> = ({
  src,
  alt,
  originalFilename,
  sha256,
  isOriginal = true,
  isVerified = true,
  dimensions,
  className = "",
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };
  const handleActualSize = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }

    if (imageRef.current) {
      const rect = imageRef.current.getBoundingClientRect();
      const clientX = e.clientX - rect.left;
      const clientY = e.clientY - rect.top;

      if (clientX >= 0 && clientX <= rect.width && clientY >= 0 && clientY <= rect.height) {
        const normX = clientX / rect.width;
        const normY = clientY / rect.height;

        const actualW = dimensions?.width || imageRef.current.naturalWidth || 1;
        const actualH = dimensions?.height || imageRef.current.naturalHeight || 1;

        setCursorPos({
          x: Math.floor(normX * actualW),
          y: Math.floor(normY * actualH),
        });
      } else {
        setCursorPos(null);
      }
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  // Wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    if (e.deltaY < 0) {
      handleZoomIn();
    } else {
      handleZoomOut();
    }
  };

  return (
    <div
      ref={containerRef}
      className={`relative flex flex-col bg-dark-950 border border-dark-800 rounded-lg overflow-hidden select-none ${className}`}
    >
      {/* Top Forensic Banner */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-dark-900 border-b border-dark-800 text-xs">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-slate-200 truncate max-w-xs">{originalFilename}</span>
          {isOriginal ? (
            <Badge variant="cyan" size="sm">
              WORM ORIGINAL
            </Badge>
          ) : (
            <Badge variant="neutral" size="sm">
              DERIVATIVE
            </Badge>
          )}
          {isVerified ? (
            <Badge variant="verified" size="sm">
              <ShieldCheck className="w-3 h-3 text-emerald-400 inline" /> SHA-256 MATCH
            </Badge>
          ) : (
            <Badge variant="compromised" size="sm">
              <ShieldAlert className="w-3 h-3 text-rose-400 inline" /> UNVERIFIED / TAMPERED
            </Badge>
          )}
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleZoomOut}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-dark-800"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-[11px] text-slate-300 min-w-10 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-dark-800"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <div className="w-px h-4 bg-dark-750 mx-1" />
          <button
            onClick={handleActualSize}
            className="px-2 py-0.5 text-[10px] font-mono text-slate-400 hover:text-white rounded hover:bg-dark-800"
            title="1:1 Pixel Ratio"
          >
            1:1
          </button>
          <button
            onClick={handleReset}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-dark-800"
            title="Reset Fit"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas Viewport */}
      <div
        className="relative flex-1 min-h-[350px] max-h-[600px] overflow-hidden flex items-center justify-center forensic-grid cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => {
          setIsDragging(false);
          setCursorPos(null);
        }}
        onWheel={handleWheel}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: "center center",
            transition: isDragging ? "none" : "transform 0.05s ease-out",
          }}
          className="inline-block"
        >
          <img
            ref={imageRef}
            src={src}
            alt={alt}
            draggable={false}
            className="max-w-none shadow-2xl rounded border border-dark-750 pointer-events-none"
            style={{ imageRendering: zoom > 2 ? "pixelated" : "auto" }}
          />
        </div>

        {/* Live Coordinate Crosshair Pill */}
        {cursorPos && (
          <div className="absolute bottom-3 left-3 bg-dark-900/90 border border-dark-700 backdrop-blur px-2.5 py-1 rounded text-[11px] font-mono text-cyan-400 flex items-center gap-1.5 shadow-lg">
            <Crosshair className="w-3 h-3 text-cyan-400" />
            <span>
              X: {cursorPos.x}px, Y: {cursorPos.y}px
            </span>
          </div>
        )}
      </div>

      {/* Bottom Forensic Metadata Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-dark-900 border-t border-dark-800 text-[11px] font-mono text-slate-400">
        <div>
          {dimensions && (
            <span>
              Resolution: {dimensions.width} &times; {dimensions.height} px
            </span>
          )}
        </div>
        {sha256 && (
          <div className="flex items-center gap-1.5 truncate max-w-md">
            <span className="text-slate-500">SHA-256:</span>
            <span className="text-slate-300 truncate">{sha256}</span>
          </div>
        )}
      </div>
    </div>
  );
};

