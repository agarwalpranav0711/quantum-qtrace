import React, { useEffect, useState } from "react";
import { Settings, RefreshCw, Database, HardDrive, Cpu, ShieldCheck, Terminal, AlertTriangle } from "lucide-react";
import { api } from "../services/api";
import { SystemInfoResponse } from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const SettingsPage: React.FC = () => {
  const [info, setInfo] = useState<SystemInfoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDiagnostics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getSystemInfo();
      setInfo(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load system diagnostics.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">System Diagnostics &amp; Settings</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time telemetry across the local database engine, physical WORM evidence storage, and Qiskit quantum simulator.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchDiagnostics}
          isLoading={isLoading}
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Refresh Telemetry
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs text-rose-300 flex items-center gap-2.5">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <LoadingSpinner label="Auditing workstation subsystem status..." size="lg" className="min-h-[300px]" />
      ) : info ? (
        <div className="space-y-6">
          {/* Subsystem Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Database Engine */}
            <Card variant="surface">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-cyan-400" />
                  <CardTitle className="text-sm">Database Engine</CardTitle>
                </div>
                <StatusIndicator status={info.database.connected ? "operational" : "compromised"} />
              </CardHeader>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">Dialect:</span>
                  <span className="text-slate-200">{info.database.dialect}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Journal Mode:</span>
                  <Badge variant={info.database.wal_mode ? "verified" : "warning"} size="sm">
                    {info.database.wal_mode ? "WAL ACTIVE" : "ROLLBACK"}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Foreign Keys:</span>
                  <span className="text-emerald-400">ENFORCED</span>
                </div>
              </div>
            </Card>

            {/* Storage Subsystem */}
            <Card variant="surface">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <HardDrive className="w-4 h-4 text-emerald-400" />
                  <CardTitle className="text-sm">Evidence Storage</CardTitle>
                </div>
                <StatusIndicator status={info.storage.accessible ? "verified" : "compromised"} />
              </CardHeader>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">WORM Policy:</span>
                  <Badge variant="verified" size="sm">
                    LOCKED (READ-ONLY)
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Subfolders:</span>
                  <span className="text-emerald-400">
                    {info.storage.directories_verified ? "6 Verified" : "Missing Subfolder"}
                  </span>
                </div>
                <div className="flex flex-col gap-0.5 pt-1">
                  <span className="text-slate-500 text-[10px]">Root Path:</span>
                  <span className="text-slate-300 truncate text-[11px]" title={info.storage.root_path}>
                    {info.storage.root_path}
                  </span>
                </div>
              </div>
            </Card>

            {/* Quantum Subsystem */}
            <Card variant="surface">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-indigo-400" />
                  <CardTitle className="text-sm">Quantum Core</CardTitle>
                </div>
                <StatusIndicator status={info.quantum.aer_simulator_available ? "operational" : "warning"} />
              </CardHeader>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">Qiskit Version:</span>
                  <span className="text-indigo-400">v{info.quantum.qiskit_version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Aer Backend:</span>
                  <span className="text-slate-200">
                    {info.quantum.aer_simulator_available ? "Available (C++)" : "Basic Simulator"}
                  </span>
                </div>
                <div className="flex flex-col gap-0.5 pt-1">
                  <span className="text-slate-500 text-[10px]">Default Target:</span>
                  <span className="text-slate-300 truncate text-[11px]" title={info.quantum.default_backend}>
                    {info.quantum.default_backend}
                  </span>
                </div>
              </div>
            </Card>
          </div>

          {/* Workstation Environment Ledger */}
          <Card variant="surface">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                <div>
                  <CardTitle>Workstation Execution Environment</CardTitle>
                  <CardDescription>Host platform specifications and application runtime parameters</CardDescription>
                </div>
              </div>
            </CardHeader>

            <div className="divide-y divide-dark-800 text-xs font-mono">
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Product Name:</span>
                <span className="text-slate-200">{info.project_name}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Application Version:</span>
                <span className="text-cyan-400 font-bold">v{info.version}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Deployment Environment:</span>
                <Badge variant="cyan" size="sm">
                  {info.environment}
                </Badge>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Host Python Runtime:</span>
                <span className="text-slate-200">Python {info.python_version}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Host Operating System:</span>
                <span className="text-slate-200">{info.platform}</span>
              </div>
              <div className="py-2.5 flex justify-between">
                <span className="text-slate-500">Local Service Address:</span>
                <span className="text-cyan-400">http://127.0.0.1:8000 (FastAPI Core)</span>
              </div>
            </div>
          </Card>
        </div>
      ) : null}
    </div>
  );
};

