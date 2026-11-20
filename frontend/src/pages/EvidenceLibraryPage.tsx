import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileImage, Search, ShieldCheck, ShieldAlert, Upload, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { EvidenceResponse } from "../types/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const EvidenceLibraryPage: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<EvidenceResponse[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [search, setSearch] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = async (targetPage = page) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.listAllEvidence(targetPage, 20);
      setEvidenceList(res.items);
      setTotal(res.total);
      setPage(res.page);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load evidence library");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence(1);
  }, []);

  const filteredEvidence = evidenceList.filter((e) => {
    const matchesSearch =
      e.original_filename.toLowerCase().includes(search.toLowerCase()) ||
      e.sha256_hash.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || e.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">Preserved Evidence Vault</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographically anchored photographic bitstreams stored under Write-Once-Read-Many (WORM) preservation rules.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => fetchEvidence(page)} leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
            Refresh Vault
          </Button>
          <Link to="/evidence/upload">
            <Button variant="primary" size="sm" leftIcon={<Upload className="w-3.5 h-3.5" />}>
              Ingest Evidence
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card variant="surface" className="p-4">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Input
              placeholder="Search by filename or SHA-256 digest..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 font-mono text-xs"
            />
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          </div>

          <div className="flex items-center gap-1.5 w-full sm:w-auto">
            {["ALL", "VERIFIED", "COMPROMISED"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 text-xs font-mono rounded-md border transition-all cursor-pointer ${
                  statusFilter === st
                    ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/40 font-semibold"
                    : "bg-dark-950 text-slate-400 border-dark-750 hover:text-slate-200"
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Grid of Evidence Cards */}
      {isLoading ? (
        <LoadingSpinner label="Auditing evidence records..." size="lg" className="min-h-[300px]" />
      ) : error ? (
        <Card variant="surface" className="p-6 text-center text-rose-400 border-rose-500/30">
          <p className="text-sm font-semibold">{error}</p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => fetchEvidence(page)}>
            Retry
          </Button>
        </Card>
      ) : filteredEvidence.length === 0 ? (
        <EmptyState
          icon={<FileImage className="w-10 h-10 text-slate-500" />}
          title={search || statusFilter !== "ALL" ? "No Matching Evidence Items" : "Evidence Vault is Empty"}
          description={
            search || statusFilter !== "ALL"
              ? "No evidence files matched the query. Try adjusting filters."
              : "Ingest your first photographic evidence file into an investigation case to establish its SHA-256 hash."
          }
          action={
            <Link to="/evidence/upload">
              <Button variant="primary" size="sm" leftIcon={<Upload className="w-3.5 h-3.5" />}>
                Ingest Photographic Evidence
              </Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredEvidence.map((item) => (
            <Card key={item.id} variant="surface" className="flex flex-col justify-between group hover:border-dark-600 transition-all">
              <div>
                {/* Visual Thumbnail */}
                <div className="h-44 bg-dark-950 rounded border border-dark-800 overflow-hidden mb-3 relative flex items-center justify-center">
                  <img
                    src={api.getEvidenceFileUrl(item.id)}
                    alt={item.original_filename}
                    className="max-h-full max-w-full object-contain"
                    onError={(evt) => {
                      (evt.target as HTMLElement).style.display = "none";
                    }}
                  />
                  <div className="absolute top-2 right-2">
                    <Badge variant={item.status === "VERIFIED" ? "verified" : "compromised"} size="sm">
                      {item.status === "VERIFIED" ? (
                        <>
                          <ShieldCheck className="w-3 h-3 inline text-emerald-400" /> VERIFIED
                        </>
                      ) : (
                        <>
                          <ShieldAlert className="w-3 h-3 inline text-rose-400" /> COMPROMISED
                        </>
                      )}
                    </Badge>
                  </div>
                </div>

                {/* Metadata */}
                <h4 className="text-xs font-semibold text-slate-100 truncate" title={item.original_filename}>
                  {item.original_filename}
                </h4>

                <div className="mt-2 space-y-1 font-mono text-[10px] text-slate-400">
                  <div className="flex justify-between">
                    <span>MIME:</span>
                    <span className="text-slate-300">{item.mime_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Dimensions:</span>
                    <span className="text-slate-300">
                      {item.width && item.height ? `${item.width} × ${item.height}` : "Unknown"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Size:</span>
                    <span className="text-slate-300">{(item.file_size / 1024).toFixed(1)} KB</span>
                  </div>
                  <div className="truncate pt-1 border-t border-dark-800">
                    <span className="text-slate-500">SHA-256:</span>{" "}
                    <span className="text-cyan-400">{item.sha256_hash.slice(0, 16)}...</span>
                  </div>
                </div>
              </div>

              {/* Action */}
              <div className="mt-4 pt-3 border-t border-dark-800 flex items-center justify-between">
                <span className="text-[10px] font-mono text-emerald-400">WORM Locked</span>
                <Link to={`/evidence/${item.id}`}>
                  <Button variant="secondary" size="sm">
                    Inspect File
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

