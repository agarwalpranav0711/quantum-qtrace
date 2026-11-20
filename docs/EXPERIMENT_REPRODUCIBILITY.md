# Q-TRACE: Scientific Experiment Reproducibility Guide

**Document Reference:** `docs/EXPERIMENT_REPRODUCIBILITY.md`  
**Classification:** Operational Runbook & Academic Reproducibility Protocol  
**Version:** 1.9.0  

---

## 1. Reproducibility Standard & Principles

To satisfy the standards of scientific peer review and judicial scrutiny, all Part 9 experimental results can be reproduced directly on any standard Windows workstation equipped with Python 3.11+.

### Key Guarantees:
- **Zero Network Dependencies:** All benchmarks run completely offline (local-first).
- **Deterministic Random Seeds:** All procedural image generators and quantum state vector simulations pin deterministic pseudo-random seeds (`seed=42`).
- **Standardized Raw Output Artifacts:** Results are exported simultaneously in human-readable Markdown/JSON and tabular CSV format under `results/part9/`.

---

## 2. Step-by-Step Instructions to Rerun Part 9 Benchmarks

Open a PowerShell terminal in the repository root directory:

### Step 1: Execute Classical Forensic Benchmark
```powershell
python experiments/part9/run_classical_benchmark.py
```
- **What it does:** Generates controlled synthetic vehicle damage panels with known ground truth masks, runs ELA, Noise, CMFD, and Consensus Fusion, and executes the JPEG quality sweep.
- **Outputs generated:**
  - `results/part9/classical/classical_benchmark_details.csv`
  - `results/part9/classical/robustness_metrics.csv`
  - `results/part9/classical/classical_benchmark_summary.json`

### Step 2: Execute Quantum Circuit & Sampling Benchmark
```powershell
python experiments/part9/run_quantum_benchmark.py
```
- **What it does:** Runs 70 sampling trials across 16Q and 12Q architectures ($S \in [64, 4096]$), computes Coupon Collector coordinate coverage, verifies unobserved `-1` handling, and performs 50-run microsecond timing breakdown.
- **Outputs generated:**
  - `results/part9/quantum/quantum_sampling_sweep.csv`
  - `results/part9/quantum/quantum_timing_breakdown.json`
  - `results/part9/quantum/quantum_benchmark_summary.json`

### Step 3: Execute Multi-Technique Ablation Study
```powershell
python experiments/part9/run_ablation_study.py
```
- **What it does:** Evaluates 9 combinations of single, pairwise, and multi-technique consensus fusion across 4 distinct attack modalities.
- **Outputs generated:**
  - `results/part9/ablation/ablation_study_matrix.csv`
  - `results/part9/ablation/ablation_study_summary.json`

### Step 4: Execute System Performance & Scaling Benchmark
```powershell
python experiments/part9/run_system_performance.py
```
- **What it does:** Benchmarks file ingestion, SHA-256 calculation, classical forensics, canvas crop/SIFT, and ReportLab PDF dossier generation across resolutions ($256 \times 256$ to $1920 \times 1080$).
- **Outputs generated:**
  - `results/part9/system/system_performance_benchmark.csv`
  - `results/part9/system/system_performance_benchmark.json`

### Step 5: Execute Automated Security Verification Suite
```powershell
python -m pytest tests/test_security_hardening.py -v
```
- **What it does:** Validates path traversal prevention, magic byte spoofing detection, decompression bomb rejection, and WORM evidence tamper detection.

