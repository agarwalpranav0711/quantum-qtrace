import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  RefreshCw,
  FolderOpen,
  Info,
  Layers,
} from "lucide-react";
import { api } from "../services/api";
import { EvidenceResponse, EvidenceVerifyResponse } from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { ForensicImageViewer } from "../components/viewer/ForensicImageViewer";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const EvidenceDetailPage: React.FC = () => {
  const { evidenceId } = useParams<{ evidenceId: string }>();

  const [evidence, setEvidence] = useState<EvidenceResponse | null>(null);
  const [verification, setVerification] = useState<EvidenceVerifyResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = async () => {
    if (!evidenceId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getEvidence(evidenceId);
      setEvidence(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load evidence details");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [evidenceId]);

  const handleVerifyIntegrity = async () => {
    if (!evidenceId) return;
    setIsVerifying(true);
    try {
      const auditResult = await api.verifyEvidence(evidenceId);
      setVerification(auditResult);
      if (evidence) {
        setEvidence({ ...evidence, status: auditResult.status });
      }
    } catch (err: unknown) {
      alert("Integrity audit failed: " + (err instanceof Error ? err.message : "Network error"));
    } finally {
      setIsVerifying(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner label="Retrieving cryptographic evidence custody file..." size="lg" className="min-h-[400px]" />;
  }

  if (error || !evidence) {
    return (
      <Card variant="surface" className="p-8 text-center text-rose-400 border-rose-500/30">
        <ShieldAlert className="w-8 h-8 mx-auto mb-2 text-rose-400" />
        <h3 className="text-base font-semibold">Evidence Record Unavailable</h3>
        <p className="text-xs text-rose-300 mt-1">{error || "Requested evidence file could not be located."}</p>
        <Link to="/evidence">
          <Button variant="secondary" size="sm" className="mt-4" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
            Return to Vault
          </Button>
        </Link>
      </Card>
    );
  }

  const fileUrl = api.getEvidenceFileUrl(evidence.id);

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb Navigation */}
      <div className="flex items-center justify-between">
        <Link
          to="/evidence"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Evidence Vault</span>
        </Link>
        <div className="flex items-center gap-2">
          <Link to={`/canvas?evidence_id=${evidence.id}`}>
            <Button variant="outline" size="sm" leftIcon={<Layers className="w-3.5 h-3.5 text-cyan-400" />}>
              Open in Forensic Canvas
            </Button>
          </Link>
          {evidence.case_id && (
            <Link to={`/investigations/${evidence.case_id}`}>
              <Button variant="outline" size="sm" leftIcon={<FolderOpen className="w-3.5 h-3.5" />}>
                Open Associated Case Dossier
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Main Forensic Image Viewer */}
      <ForensicImageViewer
        src={fileUrl}
        alt={evidence.original_filename}
        originalFilename={evidence.original_filename}
        sha256={evidence.sha256_hash}
        isOriginal={true}
        isVerified={evidence.status === "VERIFIED"}
        dimensions={
          evidence.width && evidence.height
            ? { width: evidence.width, height: evidence.height }
            : undefined
        }
      />

      {/* Two Column Layout: Cryptographic Audit vs Custody Metadata */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: On-Demand Cryptographic Audit */}
        <Card variant="surface" className="space-y-4">
          <CardHeader>
            <div>
              <CardTitle>Physical Cryptographic Audit</CardTitle>
              <CardDescription>
                Re-hash physical sectors on disk and verify bitstream invariance against ingestion record.
              </CardDescription>
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={handleVerifyIntegrity}
              isLoading={isVerifying}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            >
              Audit Bitstream Integrity
            </Button>
          </CardHeader>

          {verification ? (
            <div
              className={`p-4 rounded-lg border space-y-2.5 ${
                verification.is_intact
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-300"
              }`}
            >
              <div className="flex items-center gap-2">
                {verification.is_intact ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <ShieldAlert className="w-5 h-5 text-rose-400" />
                )}
                <span className="font-semibold text-sm">
                  {verification.is_intact ? "Bitstream Invariant (VERIFIED)" : "Integrity Failure (COMPROMISED)"}
                </span>
              </div>
              <p className="text-xs leading-relaxed">{verification.message}</p>
              <div className="pt-2 border-t border-emerald-500/20 font-mono text-[10px] space-y-1">
                <div>Audit Timestamp: {new Date(verification.verified_at).toLocaleString()}</div>
                <div className="truncate">Ingestion Hash: {verification.stored_sha256}</div>
                <div className="truncate">Disk Read Hash: {verification.current_sha256}</div>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-dark-950 rounded border border-dark-800 text-xs text-slate-400 space-y-2">
              <div className="flex items-center gap-2 text-slate-300 font-medium">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>WORM Preservation Active</span>
              </div>
              <p className="text-[11px] leading-relaxed text-slate-400">
                Operating system permissions have made this master evidence file strictly read-only. Run the cryptographic audit at any time to verify that zero byte alterations have occurred.
              </p>
            </div>
          )}

          {/* Legal / Scientific Caution Note */}
          <div className="p-3.5 bg-dark-950/70 border border-dark-800 rounded text-xs text-slate-400 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed">
              <strong className="text-slate-300">Scientific Distinction:</strong> A valid SHA-256 match proves that the physical file bytes have remained unchanged on disk since upload. It does not autonomously prove the photograph is genuine (e.g. a spliced image uploaded by a claimant retains perfect hash integrity). Use the Quantum and Classical Analysis workspaces to evaluate visual scene authenticity.
            </p>
          </div>
        </Card>

        {/* Right Column: Custody Ledger & Technical Attributes */}
        <Card variant="surface" className="space-y-4">
          <CardHeader>
            <div>
              <CardTitle>Evidence Chain of Custody Ledger</CardTitle>
              <CardDescription>Immutable technical properties recorded upon initial ingestion</CardDescription>
            </div>
            <Badge variant={evidence.status === "VERIFIED" ? "verified" : "compromised"} size="md">
              {evidence.status}
            </Badge>
          </CardHeader>

          <div className="divide-y divide-dark-800 text-xs font-mono">
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Evidence UUID:</span>
              <span className="text-slate-300 select-all">{evidence.id}</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Original Filename:</span>
              <span className="text-slate-200">{evidence.original_filename}</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Stored Filename:</span>
              <span className="text-slate-300">{evidence.stored_filename}</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Physical Storage Path:</span>
              <span className="text-slate-300 truncate max-w-xs" title={evidence.storage_path}>
                {evidence.storage_path}
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">MIME Media Type:</span>
              <span className="text-cyan-400">{evidence.mime_type}</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Byte Length:</span>
              <span className="text-slate-200">
                {evidence.file_size.toLocaleString()} bytes ({(evidence.file_size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Pixel Dimensions:</span>
              <span className="text-slate-200">
                {evidence.width && evidence.height ? `${evidence.width} × ${evidence.height} px` : "Unknown"}
              </span>
            </div>
            <div className="py-2.5 flex flex-col gap-1">
              <span className="text-slate-500">Cryptographic Digest (SHA-256):</span>
              <span className="text-cyan-300 select-all break-all bg-dark-950 p-2 rounded border border-dark-800 text-[10px]">
                {evidence.sha256_hash}
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500">Ingested Timestamp:</span>
              <span className="text-slate-300">{new Date(evidence.created_at).toLocaleString()}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

