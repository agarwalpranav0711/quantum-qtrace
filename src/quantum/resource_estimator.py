"""
Circuit resource estimation, memory scaling, and performance benchmarking module.
"""
from typing import Dict, Any, List
import time
import numpy as np

from src.classical.comparator import classical_xor_difference
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.types import CircuitResources


def calculate_raw_statevector_memory(num_qubits: int, precision_bytes: int = 16) -> Dict[str, Any]:
    """
    Computes exact raw statevector memory requirement for a given qubit count.
    
    Default precision: complex128 (16 bytes = 8 bytes real + 8 bytes imag).
    """
    num_amplitudes = 2 ** num_qubits
    total_bytes = num_amplitudes * precision_bytes
    kib = total_bytes / 1024
    mib = kib / 1024
    gib = mib / 1024
    tib = gib / 1024
    pib = tib / 1024

    # Decimal units
    kb = total_bytes / 1e3
    mb = total_bytes / 1e6
    gb = total_bytes / 1e9
    tb = total_bytes / 1e12
    pb = total_bytes / 1e15

    formatted_binary = (
        f"{pib:.2f} PiB" if pib >= 1 else
        f"{tib:.2f} TiB" if tib >= 1 else
        f"{gib:.2f} GiB" if gib >= 1 else
        f"{mib:.2f} MiB" if mib >= 1 else
        f"{kib:.2f} KiB"
    )

    formatted_decimal = (
        f"{pb:.2f} PB" if pb >= 1 else
        f"{tb:.2f} TB" if tb >= 1 else
        f"{gb:.2f} GB" if gb >= 1 else
        f"{mb:.2f} MB" if mb >= 1 else
        f"{kb:.2f} KB"
    )

    return {
        "num_qubits": num_qubits,
        "num_amplitudes": num_amplitudes,
        "total_bytes": total_bytes,
        "formatted_binary": formatted_binary,
        "formatted_decimal": formatted_decimal,
        "is_simulatable_on_laptop": num_qubits <= 28,  # ~4 GB RAM
    }


def get_memory_scaling_table() -> List[Dict[str, Any]]:
    """Generates the comprehensive memory scaling table for standard benchmark qubit counts."""
    qubits = [8, 12, 16, 18, 20, 24, 28, 30, 32, 42, 48]
    return [calculate_raw_statevector_memory(q) for q in qubits]


def benchmark_classical_vs_quantum(
    img_a: np.ndarray,
    img_b: np.ndarray,
    shots: int = 1024,
    trials: int = 10,
) -> Dict[str, Any]:
    """
    Runs repeated benchmarks comparing classical NumPy XOR against 16-qubit and 12-qubit Qiskit Aer simulation.
    
    Returns:
        Dict containing average runtimes, speedup ratios, and resource metrics.
    """
    # Classical Benchmark
    classical_times = []
    for _ in range(trials * 100):  # Run more trials since classical is so fast
        t0 = time.perf_counter_ns()
        _ = classical_xor_difference(img_a, img_b)
        classical_times.append(time.perf_counter_ns() - t0)
    avg_classical_ns = float(np.mean(classical_times))
    avg_classical_sec = avg_classical_ns / 1e9

    # 16-Qubit Quantum Benchmark
    comp_16 = QuantumComparator16Q(img_a, img_b)
    times_16 = []
    for _ in range(trials):
        t0 = time.perf_counter()
        _ = comp_16.run_simulation(shots=shots)
        times_16.append(time.perf_counter() - t0)
    avg_16q_sec = float(np.mean(times_16))
    res_16q = comp_16.extract_resources()

    # 12-Qubit Quantum Benchmark
    comp_12 = QuantumComparator12Q(img_a, img_b)
    times_12 = []
    for _ in range(trials):
        t0 = time.perf_counter()
        _ = comp_12.run_simulation(shots=shots)
        times_12.append(time.perf_counter() - t0)
    avg_12q_sec = float(np.mean(times_12))
    res_12q = comp_12.extract_resources()

    return {
        "shots": shots,
        "classical_mean_seconds": avg_classical_sec,
        "classical_mean_nanoseconds": avg_classical_ns,
        "quantum_16q_mean_seconds": avg_16q_sec,
        "quantum_12q_mean_seconds": avg_12q_sec,
        "classical_speedup_vs_16q": avg_16q_sec / avg_classical_sec,
        "classical_speedup_vs_12q": avg_12q_sec / avg_classical_sec,
        "resources_16q": res_16q,
        "resources_12q": res_12q,
    }

