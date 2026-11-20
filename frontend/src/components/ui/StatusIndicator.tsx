import React from "react";

export type StatusType = "operational" | "verified" | "compromised" | "warning" | "idle";

export interface StatusIndicatorProps {
  status: StatusType;
  label?: string;
  sublabel?: string;
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  sublabel,
  className = "",
}) => {
  const dotStyles: Record<StatusType, string> = {
    operational: "bg-cyan-400 shadow-[0_0_8px_rgba(0,229,255,0.7)]",
    verified: "bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.7)]",
    compromised: "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.7)] animate-pulse",
    warning: "bg-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.7)]",
    idle: "bg-slate-500",
  };

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <span className={`w-2 h-2 rounded-full shrink-0 ${dotStyles[status]}`} />
      {(label || sublabel) && (
        <div className="flex flex-col">
          {label && <span className="text-xs font-medium text-slate-200">{label}</span>}
          {sublabel && <span className="text-[10px] text-slate-400 font-mono">{sublabel}</span>}
        </div>
      )}
    </div>
  );
};

