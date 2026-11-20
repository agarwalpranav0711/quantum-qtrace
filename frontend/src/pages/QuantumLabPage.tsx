import React, { useState } from "react";
import { Cpu, Play, Sparkles, ShieldCheck, ShieldAlert, Info, Layers, Hash } from "lucide-react";
import { api } from "../services/api";
import { QuantumArchitecture, QuantumComparisonResponse } from "../types/api";
import { Card, CardHeader, CardTitle, CardDescription } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Select } from "../components/ui/Input";

const PRESETS = {
  identical: {
    name: "Identical Image Patches",
    patch_a: [
      [2, 4, 6, 8],
      [10, 12, 14, 15],
      [1, 3, 5, 7],
      [9, 11, 13, 0],
    ],
    patch_b: [
      [2, 4, 6, 8],
      [10, 12, 14, 15],
      [1, 3, 5, 7],
      [9, 11, 13, 0],
    ],
  },
  single_pixel: {
    name: "Single-Pixel Tamper",
    patch_a: [
      [0, 0, 0, 0],
      [0, 8, 8, 0],
      [0, 8, 8, 0],
      [0, 0, 0, 0],
    ],
    patch_b: [
      [0, 0, 0, 0],
      [0, 14, 8, 0], // Single altered pixel at (1, 1)
      [0, 8, 8, 0],
      [0, 0, 0, 0],
    ],
  },
  multi_pixel: {
    name: "Multi-Pixel Object Splice",
    patch_a: [
      [1, 1, 1, 1],
      [1, 5, 5, 1],
      [1, 5, 5, 1],
      [1, 1, 1, 1],
    ],
    patch_b: [
      [1, 1, 1, 1],
      [1, 12, 12, 1],
      [1, 12, 12, 1],
      [1, 1, 1, 1],
    ],
  },
  corners: {
    name: "Corner Boundary Alterations",
    patch_a: [
      [0, 5, 5, 0],
      [5, 10, 10, 5],
      [5, 10, 10, 5],
      [0, 5, 5, 0],
    ],
    patch_b: [
      [15, 5, 5, 15],
      [5, 10, 10, 5],
      [5, 10, 10, 5],
      [15, 5, 5, 15],
    ],
  },
};

export const QuantumLabPage: React.FC = () => {
  const [patchA, setPatchA] = useState<number[][]>(PRESETS.single_pixel.patch_a);
  const [patchB, setPatchB] = useState<number[][]>(PRESETS.single_pixel.patch_b);
  const [architecture, setArchitecture] = useState<QuantumArchitecture>("16q");
  const [shots, setShots] = useState<number>(1024);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [result, setResult] = useState<QuantumComparisonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [handoffNotice, setHandoffNotice] = useState<string | null>(null);

  React.useEffect(() => {
    const raw = sessionStorage.getItem("qtrace_handoff_patch");
    const rawA = sessionStorage.getItem("qtrace_handoff_patch_a");
    const rawB = sessionStorage.getItem("qtrace_handoff_patch_b");

    if (rawA || rawB) {
      try {
        if (rawA) {
          const patchAData = JSON.parse(rawA);
          if (Array.isArray(patchAData) && patchAData.length === 4) {
            setPatchA(patchAData);
          }
        }
        if (rawB) {
          const patchBData = JSON.parse(rawB);
          if (Array.isArray(patchBData) && patchBData.length === 4) {
            setPatchB(patchBData);
          }
        }
        setHandoffNotice("Imported 4×4 quantized comparison patches from Forensic Canvas.");
      } catch {
        // ignore parse error
      } finally {
        sessionStorage.removeItem("qtrace_handoff_patch_a");
        sessionStorage.removeItem("qtrace_handoff_patch_b");
        sessionStorage.removeItem("qtrace_handoff_patch");
      }
    } else if (raw) {
      try {
        const patch = JSON.parse(raw);
        if (Array.isArray(patch) && patch.length === 4) {
          setPatchA(patch);
          setHandoffNotice("Imported 4×4 quantized anomaly patch from Classical Analysis / Forensic Canvas (Patch A).");
        }
      } catch {
        // ignore parse error
      } finally {
        sessionStorage.removeItem("qtrace_handoff_patch");
      }
    }
  }, []);

  const handleApplyPreset = (key: keyof typeof PRESETS) => {
    setPatchA(PRESETS[key].patch_a);
    setPatchB(PRESETS[key].patch_b);
    setResult(null);
    setError(null);
  };

  const handlePixelChange = (
    target: "A" | "B",
    row: number,
    col: number,
    valStr: string
  ) => {
    let val = parseInt(valStr, 10);
    if (isNaN(val)) val = 0;
    val = Math.max(0, Math.min(15, val));

    if (target === "A") {
      const next = patchA.map((r, rIdx) =>
        r.map((c, cIdx) => (rIdx === row && cIdx === col ? val : c))
      );
      setPatchA(next);
    } else {
      const next = patchB.map((r, rIdx) =>
        r.map((c, cIdx) => (rIdx === row && cIdx === col ? val : c))
      );
      setPatchB(next);
    }
  };

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const res = await api.compareQuantumPatches({
        patch_a: patchA,
        patch_b: patchB,
        architecture,
        shots,
      });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Quantum simulation failed.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-100 tracking-tight">Quantum Image Processing Laboratory</h2>
            <Badge variant="indigo" size="sm">
              Qiskit NEQR Engine
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Experimental 16-qubit &amp; 12-qubit NEQR quantum image comparison on suspect 4&times;4 photographic regions.
          </p>
        </div>

        {/* Preset Selectors */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-mono text-slate-400 mr-1">Presets:</span>
          <button
            onClick={() => handleApplyPreset("single_pixel")}
            className="px-2.5 py-1 text-xs font-mono bg-dark-900 border border-dark-700 hover:border-cyan-500 rounded text-slate-300"
          >
            Single-Pixel Tamper
          </button>
          <button
            onClick={() => handleApplyPreset("multi_pixel")}
            className="px-2.5 py-1 text-xs font-mono bg-dark-900 border border-dark-700 hover:border-cyan-500 rounded text-slate-300"
          >
            Object Splicing
          </button>
          <button
            onClick={() => handleApplyPreset("identical")}
            className="px-2.5 py-1 text-xs font-mono bg-dark-900 border border-dark-700 hover:border-cyan-500 rounded text-slate-300"
          >
            Identical Patches
          </button>
          <button
            onClick={() => handleApplyPreset("corners")}
            className="px-2.5 py-1 text-xs font-mono bg-dark-900 border border-dark-700 hover:border-cyan-500 rounded text-slate-300"
          >
            Corner Boundary
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs text-rose-300 flex items-center gap-2.5">
          <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {handoffNotice && (
        <div className="p-3.5 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-xs text-indigo-300 flex items-center gap-2.5">
          <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
          <span>{handoffNotice}</span>
        </div>
      )}

      {/* Main Grid: Dual Patch Editors & Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Patch A (Reference) */}
        <div className="lg:col-span-4 space-y-3">
          <Card variant="surface">
            <CardHeader>
              <div>
                <CardTitle>Patch A: Reference Region</CardTitle>
                <CardDescription>4&times;4 4-bit grayscale intensities [0 – 15]</CardDescription>
              </div>
              <Badge variant="cyan" size="sm">
                ORIGINAL
              </Badge>
            </CardHeader>

            <div className="grid grid-cols-4 gap-2 bg-dark-950 p-3 rounded border border-dark-800">
              {patchA.map((row, r) =>
                row.map((val, c) => (
                  <div key={`a-${r}-${c}`} className="flex flex-col items-center">
                    <input
                      type="number"
                      min={0}
                      max={15}
                      value={val}
                      onChange={(e) => handlePixelChange("A", r, c, e.target.value)}
                      className="w-full text-center py-2 text-xs font-mono font-bold bg-dark-900 border border-dark-700 rounded text-cyan-300 focus:outline-none focus:border-cyan-400"
                      style={{
                        backgroundColor: `rgba(0, 229, 255, ${0.05 + (val / 15) * 0.25})`,
                      }}
                    />
                    <span className="text-[9px] font-mono text-slate-500 mt-0.5">
                      ({r},{c})
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Center: Circuit Configuration & Controls */}
        <div className="lg:col-span-4 space-y-4">
          <Card variant="surface">
            <CardHeader>
              <div>
                <CardTitle>Circuit Configuration</CardTitle>
                <CardDescription>Quantum comparison architecture &amp; measurement shots</CardDescription>
              </div>
              <Cpu className="w-4 h-4 text-indigo-400" />
            </CardHeader>

            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-300 font-medium block mb-1">Architecture</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setArchitecture("16q")}
                    className={`p-2.5 text-left rounded border transition-all cursor-pointer ${
                      architecture === "16q"
                        ? "bg-cyan-500/15 border-cyan-500/50 text-cyan-300"
                        : "bg-dark-950 border-dark-750 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <div className="font-semibold font-mono">16-Qubit NEQR</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">Dedicated Diff Register</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setArchitecture("12q")}
                    className={`p-2.5 text-left rounded border transition-all cursor-pointer ${
                      architecture === "12q"
                        ? "bg-cyan-500/15 border-cyan-500/50 text-cyan-300"
                        : "bg-dark-950 border-dark-750 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <div className="font-semibold font-mono">12-Qubit In-Place</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">93.8% Memory Reduction</div>
                  </button>
                </div>
              </div>

              <div>
                <Select
                  label="Measurement Sampling Shots (Coupon Collector)"
                  value={shots.toString()}
                  onChange={(e) => setShots(parseInt(e.target.value, 10))}
                  options={[
                    { value: "100", label: "100 Shots (Quick sampling)" },
                    { value: "200", label: "200 Shots (99.9% complete coverage bound)" },
                    { value: "500", label: "500 Shots (High confidence)" },
                    { value: "1024", label: "1,024 Shots (Optimal standard)" },
                    { value: "2048", label: "2,048 Shots (Deep fidelity verification)" },
                  ]}
                />
              </div>

              <div className="pt-2">
                <Button
                  variant="primary"
                  size="md"
                  className="w-full justify-center"
                  onClick={handleRunSimulation}
                  isLoading={isRunning}
                  leftIcon={<Play className="w-4 h-4 fill-current" />}
                >
                  Execute Quantum Simulation
                </Button>
              </div>
            </div>
          </Card>

          {/* Transparent Research Disclaimer */}
          <div className="p-3 bg-dark-950 rounded border border-dark-800 text-[11px] text-slate-400 space-y-1.5 leading-relaxed">
            <div className="flex items-center gap-1.5 text-slate-300 font-medium">
              <Info className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>Scientific Transparency Note</span>
            </div>
            <p>
              Simulations execute locally via <strong>Qiskit AerSimulator</strong>. No quantum supremacy or exponential speedup is claimed over classical XOR difference on classical workstations; the purpose is evaluating quantum state representations (NEQR) on localized suspicious image patches.
            </p>
          </div>
        </div>

        {/* Right: Patch B (Suspect / Modified) */}
        <div className="lg:col-span-4 space-y-3">
          <Card variant="surface">
            <CardHeader>
              <div>
                <CardTitle>Patch B: Suspect Region</CardTitle>
                <CardDescription>4&times;4 4-bit grayscale intensities [0 – 15]</CardDescription>
              </div>
              <Badge variant="warning" size="sm">
                SUSPECT
              </Badge>
            </CardHeader>

            <div className="grid grid-cols-4 gap-2 bg-dark-950 p-3 rounded border border-dark-800">
              {patchB.map((row, r) =>
                row.map((val, c) => (
                  <div key={`b-${r}-${c}`} className="flex flex-col items-center">
                    <input
                      type="number"
                      min={0}
                      max={15}
                      value={val}
                      onChange={(e) => handlePixelChange("B", r, c, e.target.value)}
                      className="w-full text-center py-2 text-xs font-mono font-bold bg-dark-900 border border-dark-700 rounded text-amber-300 focus:outline-none focus:border-amber-400"
                      style={{
                        backgroundColor: `rgba(245, 158, 11, ${0.05 + (val / 15) * 0.25})`,
                      }}
                    />
                    <span className="text-[9px] font-mono text-slate-500 mt-0.5">
                      ({r},{c})
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Simulation Results Section */}
      {result && (
        <Card variant="surface" className="border-t-4 border-t-cyan-400 space-y-5 animate-in fade-in duration-200">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded text-cyan-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <CardTitle>Quantum Simulation Findings</CardTitle>
                <CardDescription>
                  Reconstructed difference maps and circuit complexity telemetry
                </CardDescription>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant={result.identical ? "verified" : "compromised"} size="md">
                {result.identical ? "IDENTICAL PATCHES" : `${result.difference_count} DIFFERING PIXELS`}
              </Badge>
              <Badge variant="cyan" size="md">
                FIDELITY: {(result.fidelity * 100).toFixed(1)}%
              </Badge>
            </div>
          </CardHeader>

          {/* Metric Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 font-mono text-xs">
            <div className="p-3 bg-dark-950 rounded border border-dark-800">
              <span className="text-[10px] text-slate-500 uppercase">Qubits</span>
              <div className="text-base font-bold text-cyan-400 mt-0.5">{result.qubits} Qubits</div>
            </div>
            <div className="p-3 bg-dark-950 rounded border border-dark-800">
              <span className="text-[10px] text-slate-500 uppercase">Circuit Depth</span>
              <div className="text-base font-bold text-slate-100 mt-0.5">{result.depth}</div>
            </div>
            <div className="p-3 bg-dark-950 rounded border border-dark-800">
              <span className="text-[10px] text-slate-500 uppercase">Total Gates</span>
              <div className="text-base font-bold text-slate-100 mt-0.5">{result.gate_count}</div>
            </div>
            <div className="p-3 bg-dark-950 rounded border border-dark-800">
              <span className="text-[10px] text-slate-500 uppercase">Sampling Coverage</span>
              <div className="text-base font-bold text-emerald-400 mt-0.5">{(result.coverage_ratio * 100).toFixed(0)}%</div>
            </div>
            <div className="p-3 bg-dark-950 rounded border border-dark-800">
              <span className="text-[10px] text-slate-500 uppercase">Shots Measured</span>
              <div className="text-base font-bold text-slate-100 mt-0.5">{result.shots_used}</div>
            </div>
            <div className="p-3 bg-dark-950 rounded border border-dark-800">
              <span className="text-[10px] text-slate-500 uppercase">Execution Time</span>
              <div className="text-base font-bold text-indigo-400 mt-0.5">{result.execution_time_ms} ms</div>
            </div>
          </div>

          {/* Difference Maps Visual Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            {/* Quantum Reconstructed Diff Map */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                <span>Quantum Reconstructed Difference Map</span>
                <span className="text-[11px] font-mono text-cyan-400">Measurement Aggregate</span>
              </div>
              <div className="grid grid-cols-4 gap-2 bg-dark-950 p-4 rounded-lg border border-dark-800">
                {result.reconstructed_diff_map.map((row, r) =>
                  row.map((val, c) => (
                    <div
                      key={`q-diff-${r}-${c}`}
                      className={`h-12 flex flex-col items-center justify-center rounded font-mono font-bold text-xs transition-colors ${
                        val > 0
                          ? "bg-rose-500/30 text-rose-300 border border-rose-500/50 shadow-sm shadow-rose-500/20"
                          : "bg-dark-900 text-slate-500 border border-dark-800"
                      }`}
                    >
                      <span>{val}</span>
                      <span className="text-[8px] text-slate-500">
                        {val > 0 ? "TAMPER" : "MATCH"}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Classical XOR Expected Ground Truth */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                <span>Classical Bitwise XOR Ground Truth</span>
                <span className="text-[11px] font-mono text-emerald-400">Deterministic A &oplus; B</span>
              </div>
              <div className="grid grid-cols-4 gap-2 bg-dark-950 p-4 rounded-lg border border-dark-800">
                {result.classical_diff_map.map((row, r) =>
                  row.map((val, c) => (
                    <div
                      key={`c-diff-${r}-${c}`}
                      className={`h-12 flex flex-col items-center justify-center rounded font-mono font-bold text-xs ${
                        val > 0
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                          : "bg-dark-900 text-slate-500 border border-dark-800"
                      }`}
                    >
                      <span>{val}</span>
                      <span className="text-[8px] text-slate-500">
                        {val > 0 ? "TAMPER" : "MATCH"}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

