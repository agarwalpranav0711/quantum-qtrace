"""
Q-TRACE Part 9: Quantum Circuit Validation, Coupon Collector & Sampling Benchmark
Evaluates 16-qubit (dedicated difference register) and 12-qubit (compact) architectures,
shot sampling sweeps (S in {64, 128, 256, 512, 1024, 2048, 4096}) across multiple seeds,
theoretical vs empirical Coupon Collector coordinate coverage, unobserved handling (-1),
and microsecond-precision timing breakdown (circuit build, simulation, measurement, reconstruction).
"""

import time
import json
import csv
import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.classical.test_data import get_standard_test_cases
from src.classical.comparator import classical_xor_difference
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import (
    reconstruct_from_counts,
    coupon_collector_expected_shots,
    coupon_collector_exact_probability,
    coupon_collector_poisson_approx,
)


def main():
    print("=" * 70)
    print("Q-TRACE Part 9: Quantum Experimental Validation & Sampling Benchmark")
    print("=" * 70)

    out_dir = PROJECT_ROOT / "results" / "part9" / "quantum"
    out_dir.mkdir(parents=True, exist_ok=True)

    test_cases = get_standard_test_cases()
    shot_sweep = [64, 128, 256, 512, 1024, 2048, 4096]
    seeds = [42, 101, 202, 303, 404]

    print(f"\n[1/3] Running Shot Sampling Sweep on 16Q & 12Q Architectures...")
    sweep_records = []
    
    # We test on single pixel and multi pixel test cases
    sample_cases = [tc for tc in test_cases if tc["case_id"] in ["TC-02-SINGLE-PIXEL", "TC-03-MULTI-PIXEL", "TC-04-MAX-DIFFERENCE"]]

    for tc in sample_cases:
        cid = tc["case_id"]
        img_a = tc["img_a"]
        img_b = tc["img_b"]
        expected_diff = classical_xor_difference(img_a, img_b)

        for shots in shot_sweep:
            for seed in seeds:
                # 16Q Run
                comp_16 = QuantumComparator16Q(img_a, img_b)
                counts_16, res_16 = comp_16.run_simulation(shots=shots, seed_simulator=seed)
                recon_16 = reconstruct_from_counts(counts_16, architecture="16-qubit", total_shots=shots)
                is_exact_16 = np.array_equal(recon_16.reconstructed_diff, expected_diff)

                # 12Q Run
                comp_12 = QuantumComparator12Q(img_a, img_b)
                counts_12, res_12 = comp_12.run_simulation(shots=shots, seed_simulator=seed)
                recon_12 = reconstruct_from_counts(counts_12, architecture="12-qubit", total_shots=shots)
                is_exact_12 = np.array_equal(recon_12.reconstructed_diff, expected_diff)

                sweep_records.append({
                    "case_id": cid,
                    "shots": shots,
                    "seed": seed,
                    "16q_observed_coords": recon_16.observed_coordinates_count,
                    "16q_unobserved_coords": len(recon_16.missing_coordinates),
                    "16q_is_exact": bool(is_exact_16),
                    "16q_runtime_ms": round(res_16.simulation_runtime_seconds * 1000.0, 3),
                    "12q_observed_coords": recon_12.observed_coordinates_count,
                    "12q_unobserved_coords": len(recon_12.missing_coordinates),
                    "12q_is_exact": bool(is_exact_12),
                    "12q_runtime_ms": round(res_12.simulation_runtime_seconds * 1000.0, 3),
                })

    print(f"  Executed {len(sweep_records)} sampling trials across architectures.")

    # Coupon Collector Theoretical vs Empirical Validation (N=16)
    print("\n[2/3] Analyzing Coupon Collector Behavior (N=16 coordinates)...")
    theoretical_expected_shots = coupon_collector_expected_shots(16)
    coupon_analysis = []
    for s in shot_sweep:
        matching = [r for r in sweep_records if r["shots"] == s]
        avg_observed_16 = float(np.mean([r["16q_observed_coords"] for r in matching]))
        full_coverage_rate_16 = float(np.mean([1.0 if r["16q_observed_coords"] == 16 else 0.0 for r in matching]))
        full_coverage_rate_12 = float(np.mean([1.0 if r["12q_observed_coords"] == 16 else 0.0 for r in matching]))
        
        prob_exact = coupon_collector_exact_probability(16, s)
        prob_poisson = coupon_collector_poisson_approx(16, s)

        coupon_analysis.append({
            "shots": s,
            "theoretical_exact_prob": round(float(prob_exact), 5),
            "theoretical_poisson_approx": round(float(prob_poisson), 5),
            "empirical_16q_avg_observed": round(avg_observed_16, 2),
            "empirical_16q_full_coverage_pct": round(full_coverage_rate_16 * 100.0, 1),
            "empirical_12q_full_coverage_pct": round(full_coverage_rate_12 * 100.0, 1),
        })

    # Precise Microsecond Timing Breakdown
    print("\n[3/3] Performing High-Resolution Microsecond Timing Breakdown...")
    tc = [t for t in test_cases if t["case_id"] == "TC-02-SINGLE-PIXEL"][0]
    img_a, img_b = tc["img_a"], tc["img_b"]

    timing_runs = 50
    # Classical Baseline
    classical_times_us = []
    for _ in range(timing_runs):
        t0 = time.perf_counter()
        _ = classical_xor_difference(img_a, img_b)
        classical_times_us.append((time.perf_counter() - t0) * 1e6)

    # 16Q Breakdown
    build_times_ms_16 = []
    sim_times_ms_16 = []
    recon_times_ms_16 = []

    for _ in range(15):
        comp = QuantumComparator16Q(img_a, img_b)
        t0 = time.perf_counter()
        qc = comp.build_circuit(with_measurements=True)
        build_times_ms_16.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        counts, res = comp.run_simulation(shots=1024, seed_simulator=42)
        sim_times_ms_16.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        _ = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)
        recon_times_ms_16.append((time.perf_counter() - t0) * 1000.0)

    timing_breakdown = {
        "classical_xor_mean_us": round(float(np.mean(classical_times_us)), 2),
        "classical_xor_std_us": round(float(np.std(classical_times_us)), 2),
        "16q_circuit_build_mean_ms": round(float(np.mean(build_times_ms_16)), 2),
        "16q_aer_simulation_mean_ms": round(float(np.mean(sim_times_ms_16)), 2),
        "16q_reconstruction_mean_ms": round(float(np.mean(recon_times_ms_16)), 2),
        "16q_total_pipeline_mean_ms": round(
            float(np.mean(build_times_ms_16) + np.mean(sim_times_ms_16) + np.mean(recon_times_ms_16)), 2
        ),
        "classical_speed_advantage_ratio": round(
            float((np.mean(build_times_ms_16) + np.mean(sim_times_ms_16) + np.mean(recon_times_ms_16)) * 1000.0 / np.mean(classical_times_us)), 1
        )
    }

    # Save outputs
    sweep_csv = out_dir / "quantum_sampling_sweep.csv"
    with open(sweep_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(sweep_records[0].keys()))
        writer.writeheader()
        writer.writerows(sweep_records)

    timing_json = out_dir / "quantum_timing_breakdown.json"
    with open(timing_json, "w", encoding="utf-8") as f:
        json.dump(timing_breakdown, f, indent=2)

    summary_json = out_dir / "quantum_benchmark_summary.json"
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "coupon_collector_expected_shots": round(theoretical_expected_shots, 2),
        "coupon_collector_analysis": coupon_analysis,
        "timing_breakdown": timing_breakdown,
        "sample_evaluations_count": len(sweep_records),
    }
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n[OK] Results saved to {out_dir}:")
    print(f"  - {sweep_csv.name}")
    print(f"  - {timing_json.name}")
    print(f"  - {summary_json.name}")
    print(f"  Timing highlight: Classical = {timing_breakdown['classical_xor_mean_us']} us | Quantum 16Q = {timing_breakdown['16q_total_pipeline_mean_ms']} ms ({timing_breakdown['classical_speed_advantage_ratio']}x slower)")
    print("Quantum benchmark complete.")


if __name__ == "__main__":
    main()
