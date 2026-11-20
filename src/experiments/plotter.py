"""
Plotting and visualization module for Q-TRACE Part 2.
Generates publication-quality charts and circuit diagrams.
"""
from pathlib import Path
from typing import Dict, Any, List
import json
import matplotlib.pyplot as plt
import numpy as np

from src.classical.test_data import get_standard_test_cases
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q


def plot_coupon_collector_curves(
    data_json_path: str = "results/data/coupon_collector_experiment.json",
    output_png_path: str = "results/figures/coupon_collector_curve.png",
) -> None:
    """Plots exact, Poisson, and empirical Coupon Collector probabilities vs shot count."""
    with open(data_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = [d["shots"] for d in data]
    exact_p = [d["exact_prob_full_coverage"] for d in data]
    poisson_p = [d["poisson_prob_full_coverage"] for d in data]
    empirical_p = [d["empirical_prob_full_coverage"] for d in data]

    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.plot(shots, exact_p, label="Exact Analytic P (Inclusion-Exclusion)", color="#00E5FF", linewidth=2.5)
    plt.plot(shots, poisson_p, label="Poisson Tail Approx P", color="#818CF8", linestyle="--", linewidth=2.0)
    plt.scatter(shots, empirical_p, label="Empirical Observed P (50 Trials)", color="#F59E0B", s=60, zorder=5)

    # Highlight key thresholds
    plt.axvline(x=54.1, color="#EF4444", linestyle=":", alpha=0.8, label="Expected Shots E[T] = 54.1")
    plt.axvline(x=150, color="#10B981", linestyle=":", alpha=0.8, label="99.9% Complete Threshold S = 150")
    plt.axhline(y=0.999, color="#10B981", linestyle=":", alpha=0.4)

    plt.title("Coupon Collector Coverage Probability vs Measurement Shots (N = 16)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Measurement Shots (S)", fontsize=11)
    plt.ylabel("Probability of 100% Coordinate Coverage", fontsize=11)
    plt.ylim(-0.05, 1.05)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="lower right", framealpha=0.9)
    plt.tight_layout()

    out_p = Path(output_png_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_p)
    plt.close()


def plot_observed_coordinates(
    data_json_path: str = "results/data/coupon_collector_experiment.json",
    output_png_path: str = "results/figures/observed_coordinates_curve.png",
) -> None:
    """Plots mean observed coordinates out of 16 vs measurement shots."""
    with open(data_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = [d["shots"] for d in data]
    mean_obs = [d["mean_observed_coordinates"] for d in data]
    std_obs = [d["std_observed_coordinates"] for d in data]

    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.plot(shots, mean_obs, color="#00E5FF", linewidth=2.5, marker="o", label="Mean Observed Coordinates (out of 16)")
    plt.fill_between(
        shots,
        np.array(mean_obs) - np.array(std_obs),
        np.array(mean_obs) + np.array(std_obs),
        color="#00E5FF",
        alpha=0.2,
        label="±1 Standard Deviation",
    )
    plt.axhline(y=16.0, color="#10B981", linestyle="--", label="Complete Coverage (16/16)")
    plt.axvline(x=54.1, color="#EF4444", linestyle=":", label="E[T] = 54.1 shots")
    plt.axvline(x=150, color="#10B981", linestyle=":", label="99.9% Threshold S = 150")

    plt.title("Sampled Pixel Coverage vs Shot Count (4x4 Image Grid)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Measurement Shots (S)", fontsize=11)
    plt.ylabel("Observed Coordinate Count (Max 16)", fontsize=11)
    plt.ylim(6, 16.5)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="lower right", framealpha=0.9)
    plt.tight_layout()

    out_p = Path(output_png_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_p)
    plt.close()


def plot_memory_scaling(
    output_png_path: str = "results/figures/memory_scaling_curve.png",
) -> None:
    """Plots exponential statevector memory scaling on log scale with real-world physical limits."""
    qubits = np.array([8, 12, 16, 18, 20, 24, 28, 30, 32, 42, 48])
    mem_bytes = (2.0 ** qubits) * 16.0  # complex128

    plt.figure(figsize=(10, 6), dpi=300)
    plt.semilogy(qubits, mem_bytes, marker="s", color="#818CF8", linewidth=2.5, label="Raw Statevector RAM (complex128)")

    # Annotation lines
    plt.axhline(y=16 * (1024**3), color="#10B981", linestyle="--", label="16 GB Laptop RAM Limit (Q ≈ 30)")
    plt.axhline(y=64 * (1024**4), color="#F59E0B", linestyle="--", label="64 TiB (512x512 NEQR, Q = 42)")
    plt.axhline(y=4096 * (1024**4), color="#EF4444", linestyle="--", label="4.0 PiB / 4.5 PB (12 MP Image, Q = 48)")

    # Scatter points for key Q-TRACE milestones
    plt.scatter([16], [(2**16)*16], color="#00E5FF", s=120, zorder=5, label="Q-TRACE 16-Qubit Engine (1.05 MB)")
    plt.scatter([12], [(2**12)*16], color="#10B981", s=120, zorder=5, label="Q-TRACE 12-Qubit Engine (64 KB)")

    plt.title("Quantum Statevector Memory Scaling vs Qubit Count", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Total Qubits (Q)", fontsize=11)
    plt.ylabel("Memory Requirement in Bytes (Log Scale)", fontsize=11)
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend(loc="upper left", framealpha=0.9)
    plt.tight_layout()

    out_p = Path(output_png_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_p)
    plt.close()


def plot_gate_count_comparison(
    output_png_path: str = "results/figures/circuit_gate_breakdown.png",
) -> None:
    """Bar chart comparing gate counts by type for 16-qubit vs 12-qubit architectures."""
    tc = get_standard_test_cases()[1]
    comp_16 = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    comp_12 = QuantumComparator12Q(tc["img_a"], tc["img_b"])

    res_16 = comp_16.extract_resources()
    res_12 = comp_12.extract_resources()

    categories = ["Hadamard (H)", "Pauli-X", "CNOT (CX)", "MCX (Intensity)", "Measure"]
    counts_16 = [
        res_16.gate_counts_by_type.get("h", 0),
        res_16.gate_counts_by_type.get("x", 0),
        res_16.gate_counts_by_type.get("cx", 0),
        res_16.gate_counts_by_type.get("mcx", 0),
        res_16.gate_counts_by_type.get("measure", 0),
    ]
    counts_12 = [
        res_12.gate_counts_by_type.get("h", 0),
        res_12.gate_counts_by_type.get("x", 0),
        res_12.gate_counts_by_type.get("cx", 0),
        res_12.gate_counts_by_type.get("mcx", 0),
        res_12.gate_counts_by_type.get("measure", 0),
    ]

    x = np.arange(len(categories))
    width = 0.35

    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.bar(x - width/2, counts_16, width, label="16-Qubit Dedicated Register", color="#00E5FF")
    plt.bar(x + width/2, counts_12, width, label="12-Qubit In-Place Register", color="#818CF8")

    plt.title("Gate Breakdown by Type: 16-Qubit vs 12-Qubit Comparison Engine", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Gate Type", fontsize=11)
    plt.ylabel("Gate Count", fontsize=11)
    plt.xticks(x, categories, rotation=15)
    plt.grid(True, linestyle="--", alpha=0.3, axis="y")
    plt.legend(framealpha=0.9)
    plt.tight_layout()

    out_p = Path(output_png_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_p)
    plt.close()


def export_circuit_text_diagrams(output_dir: str = "results/figures") -> Dict[str, str]:
    """Generates ASCII and text circuit diagrams for 16-qubit and 12-qubit circuits."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    tc = get_standard_test_cases()[1]
    comp_16 = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    comp_12 = QuantumComparator12Q(tc["img_a"], tc["img_b"])

    qc_16 = comp_16.build_circuit(with_measurements=True)
    qc_12 = comp_12.build_circuit(with_measurements=True)

    txt_16_path = out_path / "circuit_diagram_16q.txt"
    txt_12_path = out_path / "circuit_diagram_12q.txt"

    with open(txt_16_path, "w", encoding="utf-8") as f:
        f.write("=== Q-TRACE 16-QUBIT NEQR IMAGE COMPARISON CIRCUIT ===\n")
        f.write(qc_16.draw(output="text").single_string())

    with open(txt_12_path, "w", encoding="utf-8") as f:
        f.write("=== Q-TRACE 12-QUBIT NEQR IN-PLACE COMPARISON CIRCUIT ===\n")
        f.write(qc_12.draw(output="text").single_string())

    return {
        "circuit_16q_text": str(txt_16_path),
        "circuit_12q_text": str(txt_12_path),
    }


def generate_all_figures() -> None:
    """Orchestrates generation of all research figures."""
    plot_coupon_collector_curves()
    plot_observed_coordinates()
    plot_memory_scaling()
    plot_gate_count_comparison()
    export_circuit_text_diagrams()

