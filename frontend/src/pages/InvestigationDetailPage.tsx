import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  FileImage,
  Upload,
  Calendar,
  MessageSquare,
  ShieldCheck,
  ShieldAlert,
  FolderOpen,
  RefreshCw,
  Plus,
} from "lucide-react";
import { api } from "../services/api";
import { CaseDetailResponse, CaseStatus, EvidenceResponse, ExaminerNoteResponse } from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Tabs } from "../components/ui/Tabs";
import { Modal } from "../components/ui/Modal";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { Input } from "../components/ui/Input";

export const InvestigationDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();

  const [caseData, setCaseData] = useState<CaseDetailResponse | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceResponse[]>([]);
  const [activeTab, setActiveTab] = useState<string>("evidence");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // New Note State
  const [noteContent, setNoteContent] = useState<string>("");
  const [noteAuthor, setNoteAuthor] = useState<string>("Lead Examiner");
  const [isAddingNote, setIsAddingNote] = useState<boolean>(false);

  // Upload Evidence Modal State
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fetchDetails = async () => {
    if (!caseId) return;
    setIsLoading(true);
    setError(null);
    try {
      const [caseRes, evidenceRes] = await Promise.all([
        api.getCase(caseId),
        api.listCaseEvidence(caseId),
      ]);
      setCaseData(caseRes);
      setEvidenceList(evidenceRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load case details";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [caseId]);

  const handleStatusChange = async (newStatus: CaseStatus) => {
    if (!caseId) return;
    try {
      const updated = await api.updateCase(caseId, { status: newStatus });
      setCaseData((prev) => (prev ? { ...prev, status: updated.status } : null));
    } catch (err: unknown) {
      alert("Failed to update status: " + (err instanceof Error ? err.message : "Unknown error"));
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !noteContent.trim()) return;

    setIsAddingNote(true);
    try {
      const createdNote = await api.addNote(caseId, {
        content: noteContent.trim(),
        author: noteAuthor.trim() || "Examiner",
      });
      setCaseData((prev) =>
        prev ? { ...prev, notes: [...prev.notes, createdNote] } : null
      );
      setNoteContent("");
    } catch (err: unknown) {
      alert("Failed to record examiner note: " + (err instanceof Error ? err.message : "Unknown error"));
    } finally {
      setIsAddingNote(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !selectedFile) return;

    setIsUploading(true);
    setUploadError(null);
    try {
      const uploaded = await api.uploadEvidence(caseId, selectedFile);
      setEvidenceList((prev) => [...prev, uploaded]);
      setIsUploadOpen(false);
      setSelectedFile(null);
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner label="Loading investigation dossier..." size="lg" className="min-h-[400px]" />;
  }

  if (error || !caseData) {
    return (
      <Card variant="surface" className="p-8 text-center text-rose-400 border-rose-500/30">
        <ShieldAlert className="w-8 h-8 mx-auto mb-2 text-rose-400" />
        <h3 className="text-base font-semibold">Investigation File Not Found</h3>
        <p className="text-xs text-rose-300 mt-1">{error || "Requested case identifier does not exist."}</p>
        <Link to="/investigations">
          <Button variant="secondary" size="sm" className="mt-4" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
            Return to Register
          </Button>
        </Link>
      </Card>
    );
  }

  const tabs = [
    { id: "evidence", label: "Preserved Evidence", count: evidenceList.length, icon: <FileImage /> },
    { id: "notes", label: "Examiner Observations", count: caseData.notes.length, icon: <MessageSquare /> },
    { id: "analyses", label: "Forensic Analysis Runs", count: 0, icon: <FolderOpen /> },
  ];

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          to="/investigations"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Investigations Register</span>
        </Link>
        <Button variant="ghost" size="sm" onClick={fetchDetails} leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
          Reload Dossier
        </Button>
      </div>

      {/* Case Header Card */}
      <Card variant="surface" className="border-l-4 border-l-cyan-400">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-3">
              <span className="font-mono text-sm font-bold text-cyan-400 tracking-wider">
                {caseData.case_number}
              </span>
              <Badge variant={caseData.status === "OPEN" ? "open" : "neutral"} size="md">
                {caseData.status}
              </Badge>
            </div>
            <h2 className="text-lg font-bold text-slate-100 tracking-tight">{caseData.title}</h2>
            <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
              {caseData.description || "No formal incident summary recorded for this claim."}
            </p>
          </div>

          {/* Status Switcher & Date */}
          <div className="flex flex-col md:items-end gap-2 text-xs text-slate-400">
            <div className="flex items-center gap-1.5 font-mono text-[11px]">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <span>Created: {new Date(caseData.created_at).toLocaleDateString()}</span>
            </div>

            <div className="flex items-center gap-1 mt-1">
              <span className="text-[11px] text-slate-500 mr-1">Status:</span>
              {(["OPEN", "IN_PROGRESS", "CLOSED", "ARCHIVED"] as CaseStatus[]).map((st) => (
                <button
                  key={st}
                  onClick={() => handleStatusChange(st)}
                  className={`px-2 py-0.5 text-[10px] font-mono rounded border transition-colors ${
                    caseData.status === st
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold"
                      : "bg-dark-900 text-slate-400 border-dark-750 hover:text-slate-200"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Main Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab 1: Evidence Items */}
      {activeTab === "evidence" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Preserved Evidence Items</h3>
              <p className="text-xs text-slate-400">Original photographs locked under WORM preservation policies.</p>
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsUploadOpen(true)}
              leftIcon={<Upload className="w-3.5 h-3.5" />}
            >
              Ingest Image Evidence
            </Button>
          </div>

          {evidenceList.length === 0 ? (
            <EmptyState
              icon={<FileImage className="w-10 h-10 text-slate-500" />}
              title="No Evidence Ingested in this Case"
              description="Upload the claimant's damage photograph to calculate its cryptographic SHA-256 hash and enable forensic analysis."
              action={
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setIsUploadOpen(true)}
                  leftIcon={<Upload className="w-3.5 h-3.5" />}
                >
                  Ingest First Evidence File
                </Button>
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {evidenceList.map((e) => (
                <Card key={e.id} variant="surface" className="flex flex-col justify-between group hover:border-dark-600 transition-all">
                  <div>
                    {/* Thumbnail Preview */}
                    <div className="h-40 bg-dark-950 rounded border border-dark-800 overflow-hidden mb-3 relative flex items-center justify-center">
                      <img
                        src={api.getEvidenceFileUrl(e.id)}
                        alt={e.original_filename}
                        className="max-h-full max-w-full object-contain"
                        onError={(evt) => {
                          (evt.target as HTMLElement).style.display = "none";
                        }}
                      />
                      <div className="absolute top-2 right-2">
                        <Badge variant={e.status === "VERIFIED" ? "verified" : "compromised"} size="sm">
                          {e.status}
                        </Badge>
                      </div>
                    </div>

                    <h4 className="text-xs font-semibold text-slate-100 truncate">{e.original_filename}</h4>
                    <div className="mt-1.5 space-y-1 font-mono text-[10px] text-slate-400">
                      <div className="flex justify-between">
                        <span>Dimensions:</span>
                        <span className="text-slate-300">
                          {e.width && e.height ? `${e.width} × ${e.height} px` : "Unknown"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>File Size:</span>
                        <span className="text-slate-300">{(e.file_size / 1024).toFixed(1)} KB</span>
                      </div>
                      <div className="truncate">
                        <span className="text-slate-500">SHA:</span> {e.sha256_hash.slice(0, 16)}...
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-dark-800 flex items-center justify-between">
                    <span className="text-[10px] font-mono text-slate-500">WORM Locked</span>
                    <Link to={`/evidence/${e.id}`}>
                      <Button variant="secondary" size="sm">
                        Inspect Evidence
                      </Button>
                    </Link>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Examiner Notes */}
      {activeTab === "notes" && (
        <div className="space-y-6">
          {/* Note Input Card */}
          <Card variant="surface">
            <CardHeader>
              <CardTitle>Record Examiner Observation</CardTitle>
              <CardDescription>
                Chronicle investigative findings, visual review anomalies, and interview statements.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleAddNote} className="space-y-3">
              <div className="flex gap-3">
                <div className="w-1/3">
                  <Input
                    label="Examiner Role / Name"
                    value={noteAuthor}
                    onChange={(e) => setNoteAuthor(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1.5">Observation Notes</label>
                <textarea
                  rows={3}
                  placeholder="Record observed damage inconsistencies, lighting mismatches, or suspicious edge boundaries..."
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-dark-950 text-slate-100 rounded-md border border-dark-700 focus:border-cyan-500 focus:outline-none"
                  required
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" variant="primary" size="sm" isLoading={isAddingNote} leftIcon={<Plus className="w-3.5 h-3.5" />}>
                  Save Observation
                </Button>
              </div>
            </form>
          </Card>

          {/* Notes History */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono uppercase text-slate-400 tracking-wider">Audit Log &amp; Observations</h4>
            {caseData.notes.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No notes recorded yet for this investigation file.</p>
            ) : (
              caseData.notes.map((n) => (
                <Card key={n.id} variant="flat" className="p-4 space-y-1.5 border-l-2 border-l-cyan-500/50">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span className="font-semibold text-cyan-300">{n.author}</span>
                    <span>{new Date(n.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">{n.content}</p>
                </Card>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Analysis Runs */}
      {activeTab === "analyses" && (
        <Card variant="surface" className="p-8 text-center space-y-3">
          <FolderOpen className="w-8 h-8 text-slate-500 mx-auto" />
          <h4 className="text-sm font-semibold text-slate-200">Automated Forensic Pipelines</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Full-image Classical Forensic Pipelines (Error Level Analysis, Noise Inconsistency, and SIFT Keypoint Copy-Move) are scheduled for Part 5. High-priority 4&times;4 patches can be simulated immediately in the Quantum Laboratory.
          </p>
          <Link to="/quantum-lab">
            <Button variant="outline" size="sm">
              Launch Quantum Laboratory
            </Button>
          </Link>
        </Card>
      )}

      {/* Evidence Upload Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title="Ingest Photographic Evidence"
        description="Preserve original file bitstream under WORM immutability rules."
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4">
          {uploadError && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded text-xs text-rose-300">
              {uploadError}
            </div>
          )}

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1.5">Select Image File (JPEG, PNG, TIFF)</label>
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.tif,.tiff"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-dark-800 file:text-cyan-400 hover:file:bg-dark-750 cursor-pointer"
              required
            />
            <p className="text-[11px] text-slate-500 mt-1.5">
              Strict magic-byte inspection and decompression bomb protections are enforced. Maximum file size: 50 MB.
            </p>
          </div>

          {selectedFile && (
            <div className="p-3 bg-dark-950 rounded border border-dark-800 text-xs font-mono text-slate-300 space-y-1">
              <div>Selected: {selectedFile.name}</div>
              <div>Size: {(selectedFile.size / 1024).toFixed(1)} KB</div>
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-dark-800">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsUploadOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isUploading} disabled={!selectedFile}>
              Upload &amp; Calculate SHA-256
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

