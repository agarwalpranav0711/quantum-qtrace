import React, { forwardRef } from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = "", id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label htmlFor={inputId} className="text-xs font-medium text-slate-300">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full px-3 py-2 text-sm bg-dark-950 text-slate-100 rounded-md border ${
            error ? "border-rose-500 focus:ring-rose-500" : "border-dark-700 focus:border-cyan-500 focus:ring-cyan-500"
          } focus:outline-none focus:ring-1 transition-all placeholder:text-slate-600 disabled:opacity-50 disabled:bg-dark-900 ${className}`}
          {...props}
        />
        {error && <span className="text-[11px] text-rose-400 font-medium">{error}</span>}
        {!error && helperText && <span className="text-[11px] text-slate-500">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options?: Array<{ label: string; value: string }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, children, className = "", id, ...props }, ref) => {
    const selectId = id || props.name;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label htmlFor={selectId} className="text-xs font-medium text-slate-300">
            {label}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={`w-full px-3 py-2 text-sm bg-dark-950 text-slate-100 rounded-md border ${
            error ? "border-rose-500 focus:ring-rose-500" : "border-dark-700 focus:border-cyan-500 focus:ring-cyan-500"
          } focus:outline-none focus:ring-1 transition-all disabled:opacity-50 disabled:bg-dark-900 ${className}`}
          {...props}
        >
          {options
            ? options.map((opt) => (
                <option key={opt.value} value={opt.value} className="bg-dark-900 text-slate-100">
                  {opt.label}
                </option>
              ))
            : children}
        </select>
        {error && <span className="text-[11px] text-rose-400 font-medium">{error}</span>}
        {!error && helperText && <span className="text-[11px] text-slate-500">{helperText}</span>}
      </div>
    );
  }
);

Select.displayName = "Select";

