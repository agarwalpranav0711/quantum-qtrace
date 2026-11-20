import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Upload, FileImage, ShieldAlert, CheckCircle2 } from "lucide-react";
import { api } from "../services/api";
import { CaseResponse } from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Select } from "../components/ui/Input";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export const EvidenceUploadPage: React.FC = () => {
  const navigate = useNavigate();

  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoadingCases, setIsLoadingCases] = useState<boolean>(true);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCases = async () => {
      try {
        const res = await api.getCases(1, 100);
        setCases(res.items);
        if (res.items.length > 0) {
          setSelectedCaseId(res.items[0].id);
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load active cases list.");
      } finally {
        setIsCasesLoading(false);
      }
    };
    loadCases();
  }, []);

  const setIsCasesLoading = (val: boolean) => setIsLoadingCases(val);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 52428800) {
      setError("File exceeds maximum allowed upload size (50 MB).");
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Create local preview
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCaseId || !selectedFile) {
      setError("Please select both an investigation case and an image file.");
      return;
    }

    setIsUploading(true);
    setError(null);
    try {
      const uploaded = await api.uploadEvidence(selectedCaseId, selectedFile);
      navigate(`/evidence/${uploaded.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload and integrity lock failed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <Link
          to="/evidence"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Evidence Vault</span>
        </Link>
      </div>

      <Card variant="surface">
        <CardHeader>
          <div>
            <CardTitle>Ingest Photographic Claim Evidence</CardTitle>
            <CardDescription>
              Preserve master vehicle damage photographs with automated SHA-256 calculation and OS-level WORM immutability locks.
            </CardDescription>
          </div>
        </CardHeader>

        {error && (
          <div className="mb-5 p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-md text-xs text-rose-300 flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">Ingestion Failed:</span> {error}
            </div>
          </div>
        )}

        {isLoadingCases ? (
          <LoadingSpinner label="Loading active case register..." />
        ) : cases.length === 0 ? (
          <div className="p-6 text-center space-y-3">
            <p className="text-xs text-slate-400">
              You must register an investigation case before uploading evidence photographs.
            </p>
            <Link to="/investigations/new">
              <Button variant="primary" size="sm">
                Create First Investigation Case
              </Button>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleUploadSubmit} className="space-y-5">
            <div>
              <Select
                label="Target Investigation Case *"
                value={selectedCaseId}
                onChange={(e) => setSelectedCaseId(e.target.value)}
                options={cases.map((c) => ({
                  value: c.id,
                  label: `${c.case_number} — ${c.title} (${c.status})`,
                }))}
                required
              />
              <p className="text-[11px] text-slate-500 mt-1">
                The evidence file bitstream will be linked permanently to this case dossier.
              </p>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1.5">
                Select Forensic Image File *
              </label>
              <div className="border-2 border-dashed border-dark-700 hover:border-cyan-500/50 rounded-lg p-6 text-center transition-colors bg-dark-950/50">
                <input
                  type="file"
                  id="evidence-file"
                  accept=".jpg,.jpeg,.png,.tif,.tiff"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label
                  htmlFor="evidence-file"
                  className="flex flex-col items-center justify-center cursor-pointer select-none"
                >
                  <Upload className="w-8 h-8 text-cyan-400 mb-2" />
                  <span className="text-xs font-semibold text-slate-200">
                    Click to select or drop photograph here
                  </span>
                  <span className="text-[11px] text-slate-500 mt-1">
                    Permitted formats: JPEG, PNG, TIFF &bull; Max size: 50 MB
                  </span>
                </label>
              </div>
            </div>

            {selectedFile && (
              <div className="p-4 bg-dark-950 rounded-lg border border-dark-800 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-3">
                  {previewUrl && (
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="w-12 h-12 object-cover rounded border border-dark-700"
                    />
                  )}
                  <div>
                    <div className="font-semibold text-slate-200 truncate max-w-sm">{selectedFile.name}</div>
                    <div className="text-[11px] text-slate-400">
                      Size: {(selectedFile.size / 1024).toFixed(1)} KB &bull; Type: {selectedFile.type || "Auto-detect"}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-emerald-400 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Ready for Ingestion
                </div>
              </div>
            )}

            <div className="pt-3 border-t border-dark-800 flex items-center justify-end gap-3">
              <Link to="/evidence">
                <Button type="button" variant="ghost" size="md">
                  Cancel
                </Button>
              </Link>
              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={isUploading}
                disabled={!selectedFile || !selectedCaseId}
                leftIcon={<Upload className="w-3.5 h-3.5" />}
              >
                Upload &amp; Calculate SHA-256
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
};

