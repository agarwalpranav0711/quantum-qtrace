import React from "react";
import { Loader2 } from "lucide-react";

export interface LoadingSpinnerProps {
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = "Processing forensic data...",
  size = "md",
  className = "",
}) => {
  const sizeMap = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-2.5 p-6 text-slate-400 ${className}`}>
      <Loader2 className={`${sizeMap[size]} animate-spin text-cyan-400`} />
      {label && <span className="text-xs font-mono tracking-wider text-slate-400 uppercase">{label}</span>}
    </div>
  );
};

