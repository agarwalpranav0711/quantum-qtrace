import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Plus, Database, ShieldCheck, Cpu } from "lucide-react";
import { Button } from "../ui/Button";

interface HeaderProps {
  onNewCaseClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNewCaseClick }) => {
  const location = useLocation();

  const getBreadcrumbTitle = (pathname: string): string => {
    if (pathname === "/") return "Investigation Command Center";
    if (pathname.startsWith("/investigations/new")) return "Register New Investigation";
    if (pathname.startsWith("/investigations/")) return "Investigation File Review";
    if (pathname === "/investigations") return "Investigation Case Register";
    if (pathname.startsWith("/evidence/upload")) return "Evidence Ingestion & Hashing";
    if (pathname.startsWith("/evidence/")) return "Evidence Custody & Inspection";
    if (pathname === "/evidence") return "Preserved Evidence Library";
    if (pathname === "/analysis") return "Forensic Analysis Workspace";
    if (pathname === "/quantum-lab") return "Quantum NEQR Patch Laboratory";
    if (pathname === "/findings") return "Forensic Findings & Observations";
    if (pathname === "/reports") return "Audit Dossiers & Investigation Reports";
    if (pathname === "/settings") return "System Diagnostics & Workstation Settings";
    return "Forensic Workstation";
  };

  return (
    <header className="h-16 bg-dark-900 border-b border-dark-800 px-6 flex items-center justify-between shrink-0">
      {/* Route Title & Context */}
      <div>
        <h1 className="text-sm font-semibold text-slate-100 tracking-tight">
          {getBreadcrumbTitle(location.pathname)}
        </h1>
        <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400 mt-0.5">
          <span>Q-TRACE Workstation</span>
          <span>&rsaquo;</span>
          <span className="text-cyan-400">{location.pathname}</span>
        </div>
      </div>

      {/* Global Quick Actions */}
      <div className="flex items-center gap-3">
        {/* Quick Badges */}
        <div className="hidden lg:flex items-center gap-2 border border-dark-750 bg-dark-950 px-3 py-1 rounded text-[11px] font-mono text-slate-400">
          <Database className="w-3.5 h-3.5 text-cyan-400" />
          <span>SQLite WAL</span>
          <span className="text-dark-700">|</span>
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>WORM Locked</span>
          <span className="text-dark-700">|</span>
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span>Qiskit Aer</span>
        </div>

        {onNewCaseClick ? (
          <Button size="sm" variant="primary" leftIcon={<Plus className="w-3.5 h-3.5" />} onClick={onNewCaseClick}>
            New Investigation
          </Button>
        ) : (
          <Link to="/investigations/new">
            <Button size="sm" variant="primary" leftIcon={<Plus className="w-3.5 h-3.5" />}>
              New Investigation
            </Button>
          </Link>
        )}
      </div>
    </header>
  );
};

