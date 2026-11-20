import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Search, FolderOpen, Calendar, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { CaseResponse, CaseStatus } from "../types/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const InvestigationsPage: React.FC = () => {
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [search, setSearch] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCases = async (targetPage = page) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getCases(targetPage, pageSize);
      setCases(res.items);
      setTotal(res.total);
      setPage(res.page);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load investigations";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases(1);
  }, []);

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.case_number.toLowerCase().includes(search.toLowerCase()) ||
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      (c.description && c.description.toLowerCase().includes(search.toLowerCase()));

    const matchesStatus = statusFilter === "ALL" || c.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const totalPages = Math.ceil(total / pageSize) || 1;

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">Forensic Investigation Register</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage insurance claim fraud files, evidence dossiers, and forensic examination timelines.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => fetchCases(page)} leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
            Refresh
          </Button>
          <Link to="/investigations/new">
            <Button variant="primary" size="sm" leftIcon={<Plus className="w-3.5 h-3.5" />}>
              New Investigation
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card variant="surface" className="p-4">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Input
              placeholder="Search by case number, claim title, or keywords..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          </div>

          <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
            {["ALL", "OPEN", "IN_PROGRESS", "CLOSED", "ARCHIVED"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 text-xs font-mono rounded-md border transition-all cursor-pointer whitespace-nowrap ${
                  statusFilter === st
                    ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/40 font-semibold"
                    : "bg-dark-950 text-slate-400 border-dark-750 hover:border-dark-600 hover:text-slate-200"
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Case List Table / Cards */}
      {isLoading ? (
        <LoadingSpinner label="Loading investigation records..." size="lg" className="min-h-[300px]" />
      ) : error ? (
        <Card variant="surface" className="p-6 text-center text-rose-400 border-rose-500/30">
          <p className="text-sm font-semibold">{error}</p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => fetchCases(page)}>
            Retry
          </Button>
        </Card>
      ) : filteredCases.length === 0 ? (
        <EmptyState
          icon={<FolderOpen className="w-10 h-10 text-slate-500" />}
          title={search || statusFilter !== "ALL" ? "No Matching Investigations" : "No Investigations Recorded"}
          description={
            search || statusFilter !== "ALL"
              ? "No cases matched your filter criteria. Try adjusting your search query or status filter."
              : "Register your first motor insurance claim investigation to attach photographic evidence and run forensic algorithms."
          }
          action={
            <Link to="/investigations/new">
              <Button variant="primary" size="sm" leftIcon={<Plus className="w-3.5 h-3.5" />}>
                Create Investigation
              </Button>
            </Link>
          }
        />
      ) : (
        <Card variant="surface" className="p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-dark-950 border-b border-dark-800 text-slate-400 font-mono uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Case Number</th>
                  <th className="py-3 px-4">Investigation Title</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-800">
                {filteredCases.map((c) => (
                  <tr key={c.id} className="hover:bg-dark-850/50 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-cyan-400">
                      {c.case_number}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-100">{c.title}</div>
                      <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                        {c.description || "No description."}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={
                          c.status === "OPEN"
                            ? "open"
                            : c.status === "IN_PROGRESS"
                            ? "cyan"
                            : c.status === "CLOSED"
                            ? "closed"
                            : "neutral"
                        }
                        size="sm"
                      >
                        {c.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        <span>{formatDate(c.created_at)}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link to={`/investigations/${c.id}`}>
                        <Button variant="secondary" size="sm">
                          Review File
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-dark-800 bg-dark-950 text-xs text-slate-400">
              <div>
                Showing page <span className="font-semibold text-slate-200">{page}</span> of{" "}
                <span className="font-semibold text-slate-200">{totalPages}</span> ({total} cases total)
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => fetchCases(page - 1)}
                  leftIcon={<ChevronLeft className="w-3.5 h-3.5" />}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => fetchCases(page + 1)}
                  rightIcon={<ChevronRight className="w-3.5 h-3.5" />}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

