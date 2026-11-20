import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FolderOpen,
  FileImage,
  Cpu,
  ShieldCheck,
  ArrowRight,
  Plus,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import { api } from "../services/api";
import { CaseResponse, EvidenceResponse, SystemInfoResponse } from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const CommandCenterPage: React.FC = () => {
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceResponse[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [casesRes, evidenceRes, infoRes] = await Promise.all([
        api.getCases(1, 5),
        api.listAllEvidence(1, 5),
        api.getSystemInfo().catch(() => null),
      ]);
      setCases(casesRes.items);
      setEvidenceList(evidenceRes.items);
      setSystemInfo(infoRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load command center data";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner label="Initializing investigation command center..." size="lg" className="min-h-[400px]" />;
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/30 rounded-lg text-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-rose-300">Backend Communication Error</h4>
            <p className="text-xs text-rose-400/90">{error}</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={fetchData} leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="surface" className="flex items-center justify-between">
          <div>
            <span className="text-[11px] font-mono uppercase text-slate-400">Total Investigations</span>
            <div className="text-2xl font-bold font-mono text-slate-100 mt-1">{cases.length}</div>
          </div>
          <div className="p-3 bg-dark-800 rounded-lg text-cyan-400 border border-dark-700">
            <FolderOpen className="w-5 h-5" />
          </div>
        </Card>

        <Card variant="surface" className="flex items-center justify-between">
          <div>
            <span className="text-[11px] font-mono uppercase text-slate-400">Preserved Evidence</span>
            <div className="text-2xl font-bold font-mono text-slate-100 mt-1">{evidenceList.length}</div>
          </div>
          <div className="p-3 bg-dark-800 rounded-lg text-emerald-400 border border-dark-700">
            <FileImage className="w-5 h-5" />
          </div>
        </Card>

        <Card variant="surface" className="flex items-center justify-between">
          <div>
            <span className="text-[11px] font-mono uppercase text-slate-400">WORM Immutability</span>
            <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">LOCKED</div>
          </div>
          <div className="p-3 bg-dark-800 rounded-lg text-emerald-400 border border-dark-700">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </Card>

        <Card variant="surface" className="flex items-center justify-between">
          <div>
            <span className="text-[11px] font-mono uppercase text-slate-400">Quantum Simulator</span>
            <div className="text-2xl font-bold font-mono text-indigo-400 mt-1">16Q / 12Q</div>
          </div>
          <div className="p-3 bg-dark-800 rounded-lg text-indigo-400 border border-dark-700">
            <Cpu className="w-5 h-5" />
          </div>
        </Card>
      </div>

      {/* Primary Workspace Split: Recent Cases vs Quick Laboratory Access */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Active Investigations */}
        <div className="lg:col-span-2 space-y-4">
          <Card variant="surface">
            <CardHeader>
              <div>
                <CardTitle>Active Investigation Cases</CardTitle>
                <CardDescription>Recent photographic claim fraud reviews and incident cases</CardDescription>
              </div>
              <Link to="/investigations">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  View All
                </Button>
              </Link>
            </CardHeader>

            {cases.length === 0 ? (
              <EmptyState
                title="No Active Investigations Found"
                description="Initialize your first digital evidence investigation case to preserve claim photographs and run forensic analyses."
                action={
                  <Link to="/investigations/new">
                    <Button variant="primary" size="sm" leftIcon={<Plus className="w-3.5 h-3.5" />}>
                      Create Investigation
                    </Button>
                  </Link>
                }
              />
            ) : (
              <div className="divide-y divide-dark-800">
                {cases.map((c) => (
                  <div key={c.id} className="py-3 flex items-center justify-between hover:bg-dark-850/50 px-2 rounded transition-colors">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2.5">
                        <span className="font-mono text-xs font-semibold text-cyan-400">{c.case_number}</span>
                        <Badge variant={c.status === "OPEN" ? "open" : "neutral"} size="sm">
                          {c.status}
                        </Badge>
                      </div>
                      <h4 className="text-xs font-medium text-slate-200">{c.title}</h4>
                      <p className="text-[11px] text-slate-400 line-clamp-1">{c.description || "No description provided."}</p>
                    </div>
                    <Link to={`/investigations/${c.id}`}>
                      <Button variant="secondary" size="sm">
                        Inspect
                      </Button>
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Preserved Evidence Quick Table */}
          <Card variant="surface">
            <CardHeader>
              <div>
                <CardTitle>Recently Ingested Evidence</CardTitle>
                <CardDescription>Cryptographically locked original bitstreams</CardDescription>
              </div>
              <Link to="/evidence">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  Evidence Vault
                </Button>
              </Link>
            </CardHeader>

            {evidenceList.length === 0 ? (
              <EmptyState
                icon={<FileImage className="w-8 h-8 text-slate-500" />}
                title="No Evidence Files Ingested"
                description="Upload photographic evidence into an active case to begin cryptographic hashing and analysis."
              />
            ) : (
              <div className="divide-y divide-dark-800">
                {evidenceList.map((e) => (
                  <div key={e.id} className="py-2.5 flex items-center justify-between hover:bg-dark-850/50 px-2 rounded transition-colors text-xs">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-dark-800 rounded border border-dark-750 text-slate-300">
                        <FileImage className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-medium text-slate-200">{e.original_filename}</div>
                        <div className="font-mono text-[10px] text-slate-500 truncate max-w-xs">
                          SHA: {e.sha256_hash.slice(0, 16)}...
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={e.status === "VERIFIED" ? "verified" : "compromised"} size="sm">
                        {e.status}
                      </Badge>
                      <Link to={`/evidence/${e.id}`}>
                        <Button variant="ghost" size="sm">
                          Audit
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right Col: Quick Workflows & System Info */}
        <div className="space-y-4">
          {/* Quantum Lab Quick Card */}
          <Card variant="elevated" glow className="border-indigo-500/30">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-indigo-400">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-100">Quantum Image Lab</h4>
                <p className="text-[11px] text-slate-400">NEQR 16Q &amp; 12Q Patch Simulators</p>
              </div>
            </div>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              Experiment with coherent pixel superposition, bitwise quantum CNOT XOR subtraction, and Coupon Collector measurement reconstruction on 4&times;4 image patches.
            </p>
            <Link to="/quantum-lab">
              <Button variant="primary" size="sm" className="w-full justify-between" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                Launch Quantum Lab
              </Button>
            </Link>
          </Card>

          {/* Quick Actions */}
          <Card variant="surface">
            <CardHeader>
              <CardTitle>Workstation Actions</CardTitle>
            </CardHeader>
            <div className="space-y-2">
              <Link to="/investigations/new" className="block">
                <Button variant="secondary" size="sm" className="w-full justify-start" leftIcon={<Plus className="w-4 h-4 text-cyan-400" />}>
                  Register New Investigation
                </Button>
              </Link>
              <Link to="/evidence/upload" className="block">
                <Button variant="secondary" size="sm" className="w-full justify-start" leftIcon={<FileImage className="w-4 h-4 text-emerald-400" />}>
                  Ingest Evidence Image
                </Button>
              </Link>
              <Link to="/analysis" className="block">
                <Button variant="secondary" size="sm" className="w-full justify-start" leftIcon={<FolderOpen className="w-4 h-4 text-amber-400" />}>
                  Forensic Workspace
                </Button>
              </Link>
            </div>
          </Card>

          {/* Subsystem Readiness Card */}
          {systemInfo && (
            <Card variant="flat" className="text-xs font-mono space-y-2 text-slate-400">
              <div className="font-semibold text-slate-300 uppercase tracking-wider text-[11px] mb-2">
                Operational Subsystem Status
              </div>
              <div className="flex justify-between">
                <span>Database:</span>
                <span className="text-cyan-400">{systemInfo.database.dialect} (WAL: {systemInfo.database.wal_mode ? "ON" : "OFF"})</span>
              </div>
              <div className="flex justify-between">
                <span>Storage Root:</span>
                <span className="text-emerald-400 truncate max-w-[140px]">{systemInfo.storage.root_path}</span>
              </div>
              <div className="flex justify-between">
                <span>Qiskit Core:</span>
                <span className="text-indigo-400">v{systemInfo.quantum.qiskit_version}</span>
              </div>
              <div className="flex justify-between">
                <span>Simulator:</span>
                <span className="text-slate-200 truncate max-w-[140px]">{systemInfo.quantum.default_backend}</span>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

