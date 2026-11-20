"""
Experimental runner module for Q-TRACE Part 2.
Executes reproducible benchmarks and outputs structured JSON and CSV datasets.
"""
from typing import Dict, Any, List
import json
import csv
from pathlib import Path
import numpy as np

from src.classical.test_data import get_standard_test_cases
from src.classical.comparator import classical_xor_difference
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import (
    reconstruct_from_counts,
    coupon_collector_exact_probability,
    coupon_collector_poisson_approx,
    coupon_collector_expected_shots,
)
from src.quantum.resource_estimator import (
    get_memory_scaling_table,
    benchmark_classical_vs_quantum,
)


def run_test_case_evaluations(shots: int = 1024) -> List[Dict[str, Any]]:
    """Evaluates all 8 standard test cases across 16-qubit and 12-qubit architectures."""
    test_cases = get_standard_test_cases()
    results = []

    for tc in test_cases:
        case_id = tc["case_id"]
        img_a = tc["img_a"]
        img_b = tc["img_b"]
        expected_diff = classical_xor_difference(img_a, img_b)

        # 16-Qubit evaluation
        comp_16 = QuantumComparator16Q(img_a, img_b)
        counts_16, res_16 = comp_16.run_simulation(shots=shots, seed_simulator=42)
        recon_16 = reconstruct_from_counts(counts_16, architecture="16-qubit", total_shots=shots)
        match_16 = np.array_equal(recon_16.reconstructed_diff, expected_diff)

        # 12-Qubit evaluation
        comp_12 = QuantumComparator12Q(img_a, img_b)
        counts_12, res_12 = comp_12.run_simulation(shots=shots, seed_simulator=42)
        recon_12 = reconstruct_from_counts(counts_12, architecture="12-qubit", total_shots=shots)
        match_12 = np.array_equal(recon_12.reconstructed_diff, expected_diff)

        results.append({
            "case_id": case_id,
            "description": tc["description"],
            "expected_changed_count": tc["expected_changed_count"],
            "shots": shots,
            "16q_is_exact_match": bool(match_16),
            "16q_observed_coords": recon_16.observed_coordinates_count,
            "16q_runtime_seconds": res_16.simulation_runtime_seconds,
            "16q_gate_count": res_16.total_gate_count,
            "16q_depth": res_16.circuit_depth,
            "12q_is_exact_match": bool(match_12),
            "12q_observed_coords": recon_12.observed_coordinates_count,
            "12q_runtime_seconds": res_12.simulation_runtime_seconds,
            "12q_gate_count": res_12.total_gate_count,
            "12q_depth": res_12.circuit_depth,
        })

    return results


def run_coupon_collector_experiment(
    shot_list: List[int] = None,
    trials_per_shot: int = 50,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    Empirically evaluates the Coupon Collector phenomenon over repeated stochastic trials
    and compares empirical coverage against analytical exact and Poisson formulas.
    """
    if shot_list is None:
        shot_list = [16, 32, 54, 75, 100, 150, 155, 200, 256, 512, 1024]

    test_case = get_standard_test_cases()[1]  # Single pixel test case
    img_a, img_b = test_case["img_a"], test_case["img_b"]
    comp_16 = QuantumComparator16Q(img_a, img_b)

    rng = np.random.default_rng(seed)
    results = []

    for S in shot_list:
        observed_coords_counts = []
        full_coverage_successes = 0

        for trial_idx in range(trials_per_shot):
            trial_seed = int(rng.integers(1, 1_000_000))
            counts, _ = comp_16.run_simulation(shots=S, seed_simulator=trial_seed)
            recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=S)
            obs = recon.observed_coordinates_count
            observed_coords_counts.append(obs)
            if obs == 16:
                full_coverage_successes += 1

        empirical_prob = full_coverage_successes / trials_per_shot
        exact_prob = coupon_collector_exact_probability(16, S)
        poisson_prob = coupon_collector_poisson_approx(16, S)
        mean_coords = float(np.mean(observed_coords_counts))
        std_coords = float(np.std(observed_coords_counts))

        results.append({
            "shots": S,
            "trials": trials_per_shot,
            "mean_observed_coordinates": round(mean_coords, 3),
            "std_observed_coordinates": round(std_coords, 3),
            "empirical_prob_full_coverage": round(empirical_prob, 5),
            "exact_prob_full_coverage": round(exact_prob, 5),
            "poisson_prob_full_coverage": round(poisson_prob, 5),
            "expected_missing_pixels": round(16.0 - mean_coords, 3),
        })

    return results


def export_experiment_data(output_dir: str = "results/data") -> Dict[str, str]:
    """Runs all experiments and exports structured JSON and CSV files."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Test Case Evaluations
    tc_results = run_test_case_evaluations(shots=1024)
    tc_json_path = out_path / "test_case_evaluations.json"
    tc_csv_path = out_path / "test_case_evaluations.csv"

    with open(tc_json_path, "w", encoding="utf-8") as f:
        json.dump(tc_results, f, indent=2)

    with open(tc_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(tc_results[0].keys()))
        writer.writeheader()
        writer.writerows(tc_results)

    # 2. Coupon Collector Empirical Data
    cc_results = run_coupon_collector_experiment()
    cc_json_path = out_path / "coupon_collector_experiment.json"
    cc_csv_path = out_path / "coupon_collector_experiment.csv"

    with open(cc_json_path, "w", encoding="utf-8") as f:
        json.dump(cc_results, f, indent=2)

    with open(cc_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(cc_results[0].keys()))
        writer.writeheader()
        writer.writerows(cc_results)

    # 3. Memory Scaling Table
    mem_table = get_memory_scaling_table()
    mem_json_path = out_path / "memory_scaling_table.json"
    mem_csv_path = out_path / "memory_scaling_table.csv"

    with open(mem_json_path, "w", encoding="utf-8") as f:
        json.dump(mem_table, f, indent=2)

    with open(mem_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(mem_table[0].keys()))
        writer.writeheader()
        writer.writerows(mem_table)

    # 4. Classical vs Quantum Benchmark
    tc_sample = get_standard_test_cases()[1]
    bench_data = benchmark_classical_vs_quantum(tc_sample["img_a"], tc_sample["img_b"], shots=1024, trials=5)
    bench_json_path = out_path / "classical_vs_quantum_benchmark.json"

    # Serialize resources dataclass objects to dicts
    bench_serializable = {
        k: (v.__dict__ if hasattr(v, "__dict__") else v)
        for k, v in bench_data.items()
    }
    with open(bench_json_path, "w", encoding="utf-8") as f:
        json.dump(bench_serializable, f, indent=2)

    return {
        "test_cases_json": str(tc_json_path),
        "test_cases_csv": str(tc_csv_path),
        "coupon_collector_json": str(cc_json_path),
        "coupon_collector_csv": str(cc_csv_path),
        "memory_scaling_json": str(mem_json_path),
        "memory_scaling_csv": str(mem_csv_path),
        "benchmark_json": str(bench_json_path),
    }

