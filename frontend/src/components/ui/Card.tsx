import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "surface" | "flat" | "elevated";
  glow?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = "surface",
  glow = false,
  className = "",
  ...props
}) => {
  const variantStyles = {
    surface: "bg-dark-900 border border-dark-750",
    flat: "bg-dark-950 border border-dark-800",
    elevated: "bg-dark-850 border border-dark-700 shadow-lg shadow-black/40",
  };

  const glowStyle = glow ? "hover:border-cyan-500/40 hover:shadow-glow transition-all duration-200" : "";

  return (
    <div
      className={`rounded-lg p-5 ${variantStyles[variant]} ${glowStyle} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`flex items-center justify-between pb-3 mb-4 border-b border-dark-800 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <h3 className={`text-base font-semibold text-slate-100 tracking-tight ${className}`} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <p className={`text-xs text-slate-400 mt-0.5 ${className}`} {...props}>
    {children}
  </p>
);

