# Q-TRACE — Experimental Research Plan & Benchmarking Protocol

**Document ID:** `DOC-KB-009`  
**Classification:** Scientific Experimental Design & Evaluation Protocol  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Scope:** 12 Controlled Experiments across Classical, Quantum, and System Domains  

---

## 1. Experimental Methodology & Rigor

This experimental research plan establishes the empirical protocol for validating Q-TRACE across Parts 2 through 10. To maintain scientific integrity, **all hypotheses are explicitly designated as hypotheses to be tested, never as preordained results**.

The evaluation is organized across four experimental tracks:
- **Track 1:** Classical Forensic Algorithm Accuracy (CASIA v2.0, CoMoFoD, MICC-F220).
- **Track 2:** Quantum Circuit Correctness & Sampling Dynamics (Qiskit Aer Simulator).
- **Track 3:** Classical vs. Quantum Comparative Resource Benchmarking.
- **Track 4:** Domain-Specific Insurance Claim Scenarios (Q-TRACE-AutoDamage-Bench).

---

## 2. Standard Evaluation Metrics

```
Metric Symbol       | Formula / Definition                               | Physical / Operational Meaning
--------------------+----------------------------------------------------+---------------------------------------------
Precision (P)       | TP / (TP + FP)                                     | Ratio of correctly flagged tampered pixels
Recall (R)          | TP / (TP + FN)                                     | Proportion of total tampered pixels detected
F1 Score            | 2 * (P * R) / (P + R)                              | Harmonic mean of precision and recall
IoU (Jaccard Index) | Area(Pred \cap GT) / Area(Pred \cup GT)            | Spatial overlap accuracy of bounding box/mask
False Positive Rate | FP / (FP + TN)                                     | Rate of authentic pixels falsely flagged
Circuit Depth (D)   | Longest path of dependent gates                    | Measure of quantum execution latency
CNOT Count (C_2)    | Total two-qubit entangling gates                   | Primary driver of quantum hardware error
Shot Count (S)      | Total quantum state measurements                   | Sampling budget for statistical reconstruction
Reconstruction Acc. | (1/N) * \sum \mathbb{I}(D_recon(k) == D_exact(k))  | Pixel-level correctness of sampled map
```

---

## 3. The 12 Controlled Experiments

---

### Experiment 1: Baseline Identical Pair (Zero False-Alarm Test)

- **Research Question:** Does Q-TRACE produce zero false positives when presented with identical, pristine photographic pairs?
- **Hypothesis (H1):** Both the classical SSIM difference pipeline and the 16-qubit quantum difference circuit will yield an exact zero difference map ($D = 0$ for all 16 pixels), triggering zero RoI alerts ($FPR = 0.0\%$).
- **Independent Variable:** Unmodified photographic pairs ($I_A \equiv I_B$).
- **Dependent Variables:** Detected RoI count, mean difference score, quantum Difference Flag measurement.
- **Protocol:** Feed 50 identical image pairs from CASIA v2.0 into classical and quantum comparison pipelines. Measure if any pixel is flagged as anomalous.

---

### Experiment 2: Single-Pixel Perturbation (Sensitivity Floor)

- **Research Question:** What is the minimal pixel intensity delta required for the quantum and classical engines to detect a localized change?
- **Hypothesis (H2):** The 16-qubit quantum circuit will detect a single least-significant-bit (LSB) change ($d_0 = 1$) at coordinate $(Y^*, X^*)$ with 100% mathematical fidelity once sufficient shots ($S \ge 155$) are collected. Classical subtraction will detect the same perturbation in $< 1 \text{ ms}$.
- **Independent Variable:** Modification of a single pixel $k^* = (1, 2)$ by $\Delta I \in \{1, 2, 4, 8, 15\}$.
- **Dependent Variables:** Pixel error location accuracy, quantum basis state frequency for $|k^*\rangle$, detection latency.
- **Protocol:** Invert bit 0 of pixel (1, 2) on a $4 \times 4$ tile. Execute 1024 shots. Verify if basis state $|0110\rangle_P \otimes |0001\rangle_D$ appears with theoretical frequency $\approx 1/16$.

---

### Experiment 3: Sparse Multi-Pixel Modifications (Distributed Bit Flips)

- **Research Question:** How does the distribution of quantum measurement shots behave when multiple discrete pixels are modified across a tile?
- **Hypothesis (H3):** Modifying $M \in \{2, 4, 8\}$ pixels will partition the non-zero difference outcomes into $M$ distinct basis states, each appearing with mean frequency $1/16$, while the $16-M$ unmodified pixels produce difference state $|0000\rangle_D$.
- **Independent Variable:** Number of modified pixels $M \in \{2, 4, 8\}$.
- **Dependent Variables:** Empirical shot distribution variance, reconstruction accuracy vs. $M$.

---

### Experiment 4: Continuous Geometric Region Tampering (Spliced Patch)

- **Research Question:** How accurately can the Classical Forensic Engine localize a continuous spliced vehicle damage patch?
- **Hypothesis (H4):** The weighted consensus fusion of ELA and Noise Inconsistency will localize the spliced damage polygon with an Intersection over Union (IoU) $\ge 0.75$ and an $F1 \ge 0.80$ on moderately compressed images ($Q \ge 80$).
- **Independent Variable:** Splice area ($500 \text{ px}$ to $10,000 \text{ px}$), JPEG saving quality ($Q \in \{95, 85, 75\}$).
- **Dependent Variables:** IoU, Precision, Recall, RoI bounding box centroid error.
- **Dataset:** 25 spliced cases from Q-TRACE-AutoDamage-Bench.

---

### Experiment 5: Copy-Move Damage Replication (Cloned Dent Analysis)

- **Research Question:** Can the SIFT Keypoint Engine reliably distinguish between duplicate natural vehicle components (e.g., dual headlights) and fraudulent copy-moved damage (e.g., duplicated door dents)?
- **Hypothesis (H5):** SIFT keypoint matching combined with spatial distance filtering ($d_{min} \ge 30 \text{ px}$) and affine RANSAC clustering will detect cloned dents with $Precision \ge 0.88$ on textured damage, while natural symmetrical features are filtered by coordinate clustering.
- **Independent Variable:** Rotation angle of cloned dent ($\theta \in [0^\circ, 90^\circ]$), scale factor ($s \in [0.8, 1.2]$).
- **Dependent Variables:** Matched keypoint pair count, false match rate, IoU against ground-truth mask.
- **Dataset:** CoMoFoD Small & Large categories + MICC-F220.

---

### Experiment 6: Inpainted Wear Removal (Boundary Gradient Discontinuity)

- **Research Question:** What is the limit of detectability when an investigator examines digitally inpainted (erased) vehicle rust or scratches?
- **Hypothesis (H6):** Navier-Stokes and Telea inpainting will create a drop in local Laplacian variance ($\sigma^2_L < 0.2 \cdot \bar{\sigma}^2_{ambient}$) and high-frequency noise variance, producing an anomaly flag in the Noise and Gradient modules for inpaint areas $\ge 20 \times 20$ pixels.
- **Independent Variable:** Inpainting radius ($r \in \{3, 5, 10\}$), surface texture complexity (flat painted metal vs. metallic flake).
- **Dependent Variables:** Gradient drop detection rate, boundary feathering score.
- **Dataset:** 25 inpainted wear cases from Q-TRACE-AutoDamage-Bench.

---

### Experiment 7: Dynamic Range & Quantization Sensitivity (4-bit vs. 8-bit)

- **Research Question:** What information is lost when a suspect patch is quantized from 8-bit grayscale (256 levels) to 4-bit grayscale (16 levels) for 16-qubit quantum simulation?
- **Hypothesis (H7):** 4-bit uniform quantization preserves structural damage boundaries with Mean Squared Error $\le 1.8 \times 10^{-3}$ relative to 8-bit representation, sufficient to detect any tampering whose intensity delta exceeds $\pm 16$ gray levels.
- **Independent Variable:** Quantization depth $q \in \{4, 6, 8\}$.
- **Dependent Variables:** Information entropy, structural difference preservation (SSIM).

---

### Experiment 8: Spatial Tile Scaling ($4 \times 4$ vs. $8 \times 8$ vs. $16 \times 16$)

- **Research Question:** How do circuit depth, gate count, and Qiskit Aer simulation runtime scale as patch dimensions increase?
- **Hypothesis (H8):** Gate count and state vector memory will scale exponentially: $4 \times 4$ (16 qubits, 1 MB RAM, ~150 ms runtime), $8 \times 8$ (18 qubits, 4 MB RAM, ~450 ms runtime), $16 \times 16$ (32 qubits, >68 GB RAM, simulator exhaustion on laptop).
- **Independent Variable:** Tile dimensions $N \in \{4 \times 4, 8 \times 8, 16 \times 16\}$.
- **Dependent Variables:** Qubit count, CNOT count, circuit depth, compilation time, simulation runtime.

---

### Experiment 9: Measurement Shot Count vs. Reconstruction Completeness

- **Research Question:** Does empirical quantum state reconstruction match the theoretical Coupon Collector's distribution $S \ge 155$ for $99.9\%$ completeness on a $4 \times 4$ tile?
- **Hypothesis (H9):** For shot budgets $S < 54$, missing pixels will average $> 30\%$. For $S = 256$, missing pixels will drop below $0.1\%$. For $S = 1024$, reconstruction accuracy will reach $100.0\%$.
- **Independent Variable:** Shot budget $S \in \{16, 32, 64, 128, 256, 512, 1024, 2048\}$.
- **Dependent Variables:** Observed unique state count, percentage of recovered pixels, difference map reconstruction MSE.

---

### Experiment 10: Classical vs. Quantum Comparative Resource Benchmark

- **Research Question:** What is the exact execution time and computational footprint of classical pixel XOR versus simulated quantum NEQR XOR on identical $4 \times 4$ patches?
- **Hypothesis (H10):** Classical NumPy XOR will execute in $< 50 \text{ nanoseconds}$ using $< 1 \text{ KB}$ memory. Simulated quantum XOR will require $\approx 150 \text{ milliseconds}$ and $\approx 1.05 \text{ MB}$ memory, empirically demonstrating that classical computation is millions of times faster on classical hardware, confirming Q-TRACE's honest academic stance.
- **Independent Variable:** Execution engine (NumPy CPU vs. Qiskit Aer QasmSimulator).
- **Dependent Variables:** Wall-clock execution time, peak memory usage, CPU core utilization.

---

### Experiment 11: Compression Robustness Degradation ($Q = 90, 75, 50$)

- **Research Question:** At what level of JPEG compression does each classical forensic algorithm fail to detect manipulation?
- **Hypothesis (H11):** ELA will degrade significantly below $Q = 70$ due to heavy quantization noise; Noise Inconsistency will remain effective down to $Q = 60$; SIFT copy-move detection will remain robust down to $Q = 50$.
- **Independent Variable:** JPEG quality factor $Q \in \{95, 90, 80, 70, 60, 50\}$.
- **Dependent Variables:** Precision, Recall, F1 Score per algorithm.
- **Dataset:** CoMoFoD JPEG attack benchmark subsets.

---

### Experiment 12: End-to-End Motor Insurance Claim Dossier Case Study

- **Research Question:** Can an investigator execute a complete, coherent investigation workflow on a simulated fraudulent claim, from intake to court-ready PDF generation?
- **Hypothesis (H12):** The end-to-end pipeline will ingest the claim photo, verify SHA-256 integrity, flag a spliced bumper dent via ELA/Noise consensus, route the core patch to the 16-qubit Quantum Lab for verified difference extraction, and generate a tamper-evident PDF report within 15 seconds total elapsed time.
- **Evaluation Criteria:** Complete audit trail generated; PDF contains valid SHA-256 hashes, high-resolution visual evidence, and zero runtime errors.

---

*Continue to `RISK_REGISTER.md` for the risk analysis and mitigation matrix.*

