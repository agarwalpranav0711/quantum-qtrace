import React from "react";

export type BadgeVariant =
  | "verified"
  | "compromised"
  | "warning"
  | "open"
  | "closed"
  | "cyan"
  | "indigo"
  | "neutral";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: "sm" | "md";
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  size = "md",
  className = "",
}) => {
  const sizeStyles = {
    sm: "text-[10px] px-1.5 py-0.5",
    md: "text-xs px-2.5 py-1",
  };

  const variantStyles: Record<BadgeVariant, string> = {
    verified: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    compromised: "bg-rose-500/15 text-rose-400 border border-rose-500/30",
    warning: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    open: "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30",
    closed: "bg-slate-500/15 text-slate-400 border border-slate-500/30",
    cyan: "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30",
    indigo: "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30",
    neutral: "bg-dark-800 text-slate-300 border border-dark-700",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono uppercase tracking-wider font-medium rounded ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

