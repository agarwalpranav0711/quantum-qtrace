import React from "react";
import { Link } from "react-router-dom";
import { FileSearch, ShieldCheck, Binary, MessageSquare, AlertTriangle, Info, ArrowRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";

export const FindingsPage: React.FC = () => {
  const categories = [
    {
      title: "Category 1: Directly Observed Technical Facts",
      description: "Cryptographically verifiable physical data with zero algorithmic inference or subjectivity.",
      badge: "VERIFIED FACTS",
      badgeVariant: "verified" as const,
      icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
      items: [
        {
          label: "Bitstream Hash Verification",
          value: "NIST FIPS 180-4 SHA-256 byte-for-byte matching against ingestion records.",
          status: "Mathematical Fact",
        },
        {
          label: "Original File Immutability",
          value: "WORM file permissions (read-only) enforced at operating system level.",
          status: "Physical Attribute",
        },
        {
          label: "Container Metadata",
          value: "Unmodified EXIF, pixel raster geometry, and media container signatures.",
          status: "Raw Metadata",
        },
      ],
    },
    {
      title: "Category 2: Algorithmic Simulation & Telemetry Outputs",
      description: "Outputs produced by deterministic quantum circuits and classical mathematical models.",
      badge: "ALGORITHMIC TELEMETRY",
      badgeVariant: "indigo" as const,
      icon: <Binary className="w-5 h-5 text-indigo-400" />,
      items: [
        {
          label: "Quantum NEQR Patch Fidelity",
          value: "Simulation on Qiskit Aer comparing multi-qubit color and position superpositions.",
          status: "Empirical Measure",
        },
        {
          label: "Classical Bitwise Difference",
          value: "Deterministic XOR disparity counts on 4×4 pixel neighborhoods.",
          status: "Ground Truth",
        },
        {
          label: "Coupon Collector Sampling Bounds",
          value: "Statistical shot coverage ratio verifying complete coordinate measurement.",
          status: "Probabilistic Bound",
        },
      ],
    },
    {
      title: "Category 3: Potential Manipulation Indicators",
      description: "Statistical or physical anomalies flagged for human expert examination.",
      badge: "INVESTIGATIVE LEADS",
      badgeVariant: "warning" as const,
      icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
      items: [
        {
          label: "Localized Pixel Disparity",
          value: "Differing coordinates in quantum/classical difference maps requiring contextual review.",
          status: "Flagged Region",
        },
        {
          label: "Compression Grid Artifacts",
          value: "Inconsistent 8×8 block compression boundaries (ELA scheduled in Part 5).",
          status: "Under Analysis",
        },
      ],
    },
    {
      title: "Category 4: Examiner Hypotheses & Qualitative Notes",
      description: "Human investigator observations, interview insights, and case context.",
      badge: "EXAMINER INTERPRETATION",
      badgeVariant: "cyan" as const,
      icon: <MessageSquare className="w-5 h-5 text-cyan-400" />,
      items: [
        {
          label: "Physical Context Assessment",
          value: "Evaluating whether claimed impact damage aligns with vehicular collision kinematics.",
          status: "Human Judgement",
        },
        {
          label: "Lighting & Specular Reflection Review",
          value: "Visual assessment of shadow angles, environmental reflection consistency.",
          status: "Human Judgement",
        },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-slate-100 tracking-tight">Forensic Findings &amp; Evidence Taxonomy</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Q-TRACE maintains strict separation between physical facts, algorithmic calculations, flagged anomalies, and human examiner hypotheses.
        </p>
      </div>

      {/* Ethical / Legal Admissibility Principle Banner */}
      <Card variant="flat" className="border-l-4 border-l-cyan-400 p-4 flex items-start gap-3">
        <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed text-slate-300">
          <strong className="text-slate-100 font-semibold">Core Evidentiary Principle: </strong>
          Q-TRACE does not emit an autonomous "fraud percentage" or declare a legal verdict. The platform provides decision intelligence support, verifiable mathematical telemetry, and transparent evidence preservation for forensic analysts and claim investigation teams.
        </div>
      </Card>

      {/* Taxonomy Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((cat, idx) => (
          <Card key={idx} variant="surface" className="flex flex-col justify-between">
            <div>
              <CardHeader>
                <div className="flex items-center gap-2.5">
                  <div className="p-2 bg-dark-800 rounded border border-dark-750">{cat.icon}</div>
                  <div>
                    <CardTitle className="text-sm">{cat.title}</CardTitle>
                    <CardDescription>{cat.description}</CardDescription>
                  </div>
                </div>
                <Badge variant={cat.badgeVariant} size="sm">
                  {cat.badge}
                </Badge>
              </CardHeader>

              <div className="space-y-3 pt-2">
                {cat.items.map((item, i) => (
                  <div key={i} className="p-3 bg-dark-950 rounded border border-dark-800 space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{item.label}</span>
                      <span className="text-[10px] font-mono text-slate-500 uppercase">{item.status}</span>
                    </div>
                    <p className="text-slate-400 leading-relaxed text-[11px]">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-dark-800 flex justify-end">
              <Link to="/investigations">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  Review in Cases
                </Button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

