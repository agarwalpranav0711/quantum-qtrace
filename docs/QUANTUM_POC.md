# Q-TRACE — Quantum Proof of Concept (Part 2 Implementation)

**Document ID:** `DOC-POC-001`  
**Classification:** Engineering Proof of Concept & Implementation Guide  
**Version:** 1.0.0 (Part 2 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Quantum Engineering Team  
**Runtime:** Python 3.11, Qiskit 2.6.2, Qiskit Aer 0.18.4  

---

## 1. Executive Summary

This document describes the working, mathematically validated **Quantum Proof of Concept** for Q-TRACE. 

In this phase, we implemented:
1. **The 16-Qubit Dedicated Difference Register Architecture:** A full NEQR-inspired image comparison engine maintaining distinct spatial, original intensity, modified intensity, and XOR difference registers.
2. **The 12-Qubit In-Place Difference Register Architecture:** A memory-efficient alternative performing in-place XOR comparison on the modified image register, reducing statevector simulation memory by 93.75%.
3. **An Independent Classical Comparator:** Deterministic ground-truth calculation of bitwise XOR, absolute intensity differences, and difference metrics for 4x4 4-bit grayscale image pairs.
4. **Sampling & Reconstruction Engine:** Measurement decoding, Coupon Collector probability modeling, and spatial difference map aggregation that explicitly marks unobserved coordinates without false-negative bias.
5. **A 52-Test Automated Pytest Suite:** Complete automated verification covering unit components, reversibility, edge cases, and end-to-end quantum-classical equivalence.
6. **Empirical Benchmarks & Publication Figures:** Real experimental runs generating CSV/JSON datasets, circuit diagrams, and convergence curves in `results/`.

---

## 2. Codebase Organization

The implementation is structured into modular Python packages inside `src/`:

```
d:\WebDev PROJECTS\quantum qtrace/
├── src/
│   ├── __init__.py
│   ├── classical/
│   │   ├── __init__.py
│   │   ├── comparator.py             # Classical bitwise XOR, abs diff, validation
│   │   └── test_data.py              # 8 deterministic standard test cases
│   ├── quantum/
│   │   ├── __init__.py
│   │   ├── types.py                  # Dataclasses: ReconstructionResult, CircuitResources, etc.
│   │   ├── state_prep.py             # Superposition and reversible coordinate-conditioned MCX loading
│   │   ├── circuit_16q.py            # Primary 16-qubit comparison circuit builder & runner
│   │   ├── circuit_12q.py            # 12-qubit in-place comparison circuit builder & runner
│   │   ├── reconstruction.py         # Bitstring parsing, Coupon Collector math & map reconstruction
│   │   └── resource_estimator.py     # Qubit counts, gate counts, depth, memory & CPU runtime benchmarks
│   └── experiments/
│       ├── __init__.py
│       ├── runner.py                 # Multi-shot stochastic runner, data exporter (CSV/JSON)
│       ├── plotter.py                # Matplotlib figure generator (PNG)
│       └── print_results.py          # Summary CLI display script
├── tests/
│   ├── __init__.py
│   ├── test_classical.py             # Tests for comparator, validators, and test cases (7 tests)
│   ├── test_quantum_state_prep.py    # Tests for coordinate mapping, superposition, reversibility (4 tests)
│   ├── test_quantum_16q.py           # Tests for 16-qubit engine across multiple image pairs (7 tests)
│   ├── test_quantum_12q.py           # Tests for 12-qubit engine and in-place reversibility (5 tests)
│   ├── test_reconstruction.py        # Tests for bitstring parsing and Coupon Collector math (7 tests)
│   └── test_end_to_end.py            # Parametric end-to-end integration tests (22 tests)
├── results/
│   ├── data/                         # Generated JSON & CSV benchmark files
│   └── figures/                      # Generated PNG charts & TXT circuit diagrams
└── docs/                             # Complete project documentation
```

---

## 3. Quickstart & Verification Commands

All commands run natively in Windows PowerShell in the active environment:

### Run the complete test suite:
```powershell
pytest -v
```
*Result:* 52 passed in ~3.2 seconds with zero warnings.

### Run experiments and generate figures:
```powershell
python -c "from src.experiments.runner import export_experiment_data; from src.experiments.plotter import generate_all_figures; export_experiment_data(); generate_all_figures()"
```

### Display experimental summary table:
```powershell
python src/experiments/print_results.py
```

---

## 4. Programmatic Usage Examples

### 4.1 Running the 16-Qubit Comparison Engine

```python
import numpy as np
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.reconstruction import reconstruct_from_counts
from src.classical.comparator import classical_xor_difference

# Define two 4x4 4-bit grayscale images
img_a = np.array([
    [1,  2,  3,  4],
    [5,  6,  7,  8],
    [9, 10, 11, 12],
    [13, 14, 15,  0]
], dtype=np.uint8)

img_b = img_a.copy()
img_b[1, 2] = 12  # Change pixel (1, 2) from 7 to 12

# Build and execute 16-qubit circuit on Qiskit Aer
comparator = QuantumComparator16Q(img_a, img_b)
counts, resources = comparator.run_simulation(shots=1024)

# Reconstruct 4x4 spatial difference map
recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

print("Observed Coordinates:", recon.observed_coordinates_count, "/ 16")
print("Reconstructed Difference Map:\n", recon.reconstructed_diff)
print("Expected Classical XOR:\n", classical_xor_difference(img_a, img_b))
assert np.array_equal(recon.reconstructed_diff, classical_xor_difference(img_a, img_b))
```

### 4.2 Running the 12-Qubit In-Place Comparison Engine

```python
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import reconstruct_from_counts

comparator_12q = QuantumComparator12Q(img_a, img_b)
counts_12q, resources_12q = comparator_12q.run_simulation(shots=1024)
recon_12q = reconstruct_from_counts(counts_12q, architecture="12-qubit", total_shots=1024)

print("12-Qubit Reconstructed Difference Map:\n", recon_12q.reconstructed_diff)
assert np.array_equal(recon_12q.reconstructed_diff, img_a ^ img_b)
```

---

## 5. Summary of Experimental Verification

| Metric / Test Dimension | Measured Result | Verification Status |
| :--- | :--- | :--- |
| **Test Suite Pass Rate** | **52 / 52 Passed (100%)** | **FLAWLESS** |
| **Identical Images Difference Map** | All 16 pixels strictly 0 | **VERIFIED** |
| **Single-Pixel Perturbation** | Row 1, Col 2 strictly 11 ($7 \oplus 12$), remaining 15 pixels strictly 0 | **VERIFIED** |
| **Random Trials Equivalence** | 100% bitwise identity with classical XOR across all random seeds | **VERIFIED** |
| **16-Qubit Simulation Memory** | 1.00 MiB (1.05 MB) | **VERIFIED** |
| **12-Qubit Simulation Memory** | 64.00 KiB (65.54 KB) — 93.75% reduction | **VERIFIED** |
| **Coupon Collector Expectation $E[T]$** | 54.09 shots | **VERIFIED** |
| **99.9% Full Reconstruction Budget** | $S = 150$ shots (exact), $S = 155$ shots (approx), $S = 1024$ default | **VERIFIED** |

---

*Continue to `QUANTUM_MATHEMATICS.md` for complete derivations of state representations, gate decompositions, and measurement probabilities.*

