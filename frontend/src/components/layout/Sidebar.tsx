import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderOpen,
  FileImage,
  Microscope,
  Layers,
  Cpu,
  FileSearch,
  FileText,
  Settings,
  Shield,
  Activity,
} from "lucide-react";
import { StatusIndicator } from "../ui/StatusIndicator";

interface SidebarProps {
  isHealthy: boolean;
  version: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isHealthy, version }) => {
  const navItems = [
    { to: "/", label: "Command Center", icon: <LayoutDashboard className="w-4 h-4" /> },
    { to: "/investigations", label: "Investigations", icon: <FolderOpen className="w-4 h-4" /> },
    { to: "/evidence", label: "Evidence Library", icon: <FileImage className="w-4 h-4" /> },
    { to: "/analysis", label: "Analysis Workspace", icon: <Microscope className="w-4 h-4" /> },
    { to: "/canvas", label: "Forensic Canvas", icon: <Layers className="w-4 h-4" /> },
    { to: "/quantum-lab", label: "Quantum Laboratory", icon: <Cpu className="w-4 h-4" /> },
    { to: "/findings", label: "Findings", icon: <FileSearch className="w-4 h-4" /> },
    { to: "/reports", label: "Reports", icon: <FileText className="w-4 h-4" /> },
    { to: "/settings", label: "Settings & System", icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 bg-dark-900 border-r border-dark-800 flex flex-col shrink-0 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-dark-800">
        <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <Shield className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold tracking-wider text-sm text-slate-100">Q-TRACE</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
              v{version}
            </span>
          </div>
          <p className="text-[10px] text-slate-500 truncate max-w-[150px]">Forensic Intelligence</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-500">
          Workstation Navigation
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-all duration-150 ${
                isActive
                  ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/25 shadow-sm shadow-cyan-500/5 font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-dark-850"
              }`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Subsystem Health Status Footer */}
      <div className="p-4 border-t border-dark-800 bg-dark-950/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-xs text-slate-400">Backend API</span>
          </div>
          <StatusIndicator
            status={isHealthy ? "operational" : "compromised"}
            label={isHealthy ? "ONLINE" : "OFFLINE"}
          />
        </div>
        <div className="mt-2 text-[10px] font-mono text-slate-500">
          Port 8000 &bull; Local WORM Active
        </div>
      </div>
    </aside>
  );
};

