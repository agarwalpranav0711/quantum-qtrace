import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, ShieldAlert, Sparkles } from "lucide-react";
import { api, ApiError } from "../services/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

export const CreateInvestigationPage: React.FC = () => {
  const navigate = useNavigate();

  const [caseNumber, setCaseNumber] = useState<string>("");
  const [title, setTitle] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateCaseNumber = () => {
    const year = new Date().getFullYear();
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    setCaseNumber(`QC-${year}-${randomSuffix}`);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!caseNumber.trim() || caseNumber.length < 3) {
      setError("Case number must be at least 3 characters long.");
      return;
    }

    if (!title.trim() || title.length < 3) {
      setError("Investigation title must be at least 3 characters long.");
      return;
    }

    setIsSubmitting(true);
    try {
      const created = await api.createCase({
        case_number: caseNumber.trim(),
        title: title.trim(),
        description: description.trim() || null,
      });

      navigate(`/investigations/${created.id}`);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.statusCode === 409) {
          setError(`Case number '${caseNumber}' already exists. Please choose a unique identifier.`);
        } else {
          setError(err.message);
        }
      } else {
        setError("Failed to create investigation case. Please verify backend connectivity.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Back Link */}
      <div>
        <Link
          to="/investigations"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Investigations Register</span>
        </Link>
      </div>

      <Card variant="surface">
        <CardHeader>
          <div>
            <CardTitle>Register New Investigation Case</CardTitle>
            <CardDescription>
              Create a tamper-evident dossier container to bind photographic evidence, examiner notes, and forensic analyses.
            </CardDescription>
          </div>
        </CardHeader>

        {error && (
          <div className="mb-5 p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-md text-xs text-rose-300 flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">Submission Rejected:</span> {error}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="case_number" className="text-xs font-medium text-slate-300">
                Case / Claim Number <span className="text-cyan-400">*</span>
              </label>
              <button
                type="button"
                onClick={handleGenerateCaseNumber}
                className="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1 cursor-pointer"
              >
                <Sparkles className="w-3 h-3" /> Generate Identifier
              </button>
            </div>
            <Input
              id="case_number"
              placeholder="e.g. QC-2026-7841"
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              className="font-mono text-sm uppercase tracking-wider"
              required
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Unique forensic case number used in official reports and cryptographic manifests.
            </p>
          </div>

          <div>
            <Input
              label="Investigation Title *"
              placeholder="e.g. Frontal Impact Claim — Vehicle Bumper Staging Audit"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="description" className="text-xs font-medium text-slate-300 block mb-1.5">
              Investigation Summary / Incident Details
            </label>
            <textarea
              id="description"
              rows={4}
              placeholder="Record the initial claim details, date of loss, vehicle description, and reasons for photographic audit..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-dark-950 text-slate-100 rounded-md border border-dark-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 focus:outline-none transition-all placeholder:text-slate-600"
            />
          </div>

          <div className="pt-3 border-t border-dark-800 flex items-center justify-end gap-3">
            <Link to="/investigations">
              <Button type="button" variant="ghost" size="md">
                Cancel
              </Button>
            </Link>
            <Button type="submit" variant="primary" size="md" isLoading={isSubmitting}>
              Initialize Investigation Case
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

