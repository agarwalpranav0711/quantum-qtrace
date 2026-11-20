import React from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  className = "",
  disabled,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-medium transition-all duration-150 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-950 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer select-none";

  const sizeStyles = {
    sm: "text-xs px-2.5 py-1.5 gap-1.5",
    md: "text-sm px-3.5 py-2 gap-2",
    lg: "text-base px-5 py-2.5 gap-2.5",
  };

  const variantStyles = {
    primary:
      "bg-cyan-500 hover:bg-cyan-400 text-dark-950 font-semibold focus:ring-cyan-400 shadow-sm shadow-cyan-500/20 active:bg-cyan-600",
    secondary:
      "bg-dark-800 hover:bg-dark-750 text-slate-100 border border-dark-700 hover:border-dark-600 focus:ring-dark-600 active:bg-dark-700",
    outline:
      "bg-transparent hover:bg-dark-850 text-cyan-400 border border-cyan-500/30 hover:border-cyan-500/60 focus:ring-cyan-500 active:bg-dark-800",
    danger:
      "bg-rose-600 hover:bg-rose-500 text-white font-medium focus:ring-rose-500 shadow-sm shadow-rose-600/20 active:bg-rose-700",
    ghost:
      "bg-transparent hover:bg-dark-850 text-slate-300 hover:text-white focus:ring-dark-700 active:bg-dark-800",
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-current" />
      ) : (
        leftIcon && <span className="inline-flex shrink-0">{leftIcon}</span>
      )}
      <span>{children}</span>
      {!isLoading && rightIcon && <span className="inline-flex shrink-0">{rightIcon}</span>}
    </button>
  );
};

