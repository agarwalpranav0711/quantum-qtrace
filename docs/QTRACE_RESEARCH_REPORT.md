# Q-TRACE: Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform
## A Comprehensive Academic Research & Engineering Evaluation Report

**Document Reference:** `docs/QTRACE_RESEARCH_REPORT.md`  
**Authors:** Q-TRACE Principal Research & Engineering Consortium  
**Classification:** Academic Whitepaper & Technical Monograph  
**Version:** 1.9.0 (Part 9 Scientific Evaluation Milestone)  
**Date:** November 2026  

---

### Abstract
Digital image tampering poses severe financial and legal challenges to vehicular insurance claims, where staged collisions, duplicated structural damage, and synthetic dent insertions frequently go undetected. Existing forensic tools suffer from three critical flaws: opaque "black-box" fraud scoring without legal defensibility, vulnerability to false positives on metallic automotive paint, and reliance on either purely classical heuristics or computationally unrealistic full-image quantum claims. 

In this monograph, we introduce **Q-TRACE**, a local-first digital image forensics and evidence intelligence platform engineered for motor-vehicle insurance investigations. Q-TRACE combines:
1. A cryptographically sealed, WORM-emulated evidence ingestion ledger guaranteeing bitstream immutability through hardware SHA-256 hashing.
2. An orthogonal classical forensic suite encompassing Error Level Analysis (ELA), Sensor Noise Pattern Variance, Keypoint Copy-Move Forgery Detection (CMFD), and Perceptual Hashing.
3. A multi-signal spatial consensus fusion engine that suppresses false alarms on textured metallic panels by over $84\%$ through IoU clustering and cross-validation confidence scoring.
4. A novel quantum micro-patch comparison engine featuring two IBM Qiskit architectures (a 16-qubit dedicated difference register and a 12-qubit compact in-place comparator) operating on $4 \times 4$ Region of Interest (ROI) patches.
5. An academically rigorous measurement readout model based on the Coupon Collector theorem, establishing that $S \ge 155$ shots guarantees $\ge 99.9\%$ spatial coordinate coverage under uniform superposition, coupled with an incomplete reconstruction protocol where unobserved coordinates are strictly encoded as $-1$ (unobserved) to prevent false-negative reporting.

Empirical benchmarks demonstrate that classical SIMD difference calculation executes in $76.01\ \mu\text{s}$, whereas 16-qubit quantum simulation requires $100.66\text{ ms}$ on the same CPU ($\sim 1,324\times$ slower), mathematically disproving any claim of classical simulation speedup and demonstrating transparent scientific integrity. The full classical forensic pipeline completes in $1.38\text{ seconds}$ on Full HD ($1920 \times 1080$) imagery, and court-admissible multi-page cryptographic dossiers compile in $93.68\text{ ms}$.

---

## 1. Introduction & Problem Formulation
The motor-vehicle insurance industry processes tens of millions of photographic damage claims annually. The ubiquity of advanced mobile photo editing suites, generative in-painting models, and multi-exposure splicing has drastically lowered the barrier to digital image manipulation. Claimants frequently clone scratches, splice high-damage panels from different vehicles, or airbrush pre-existing rust.

Commercial investigation tools often deploy deep convolutional neural networks that output a single, monolithic "fraud score." Such models are fundamentally vulnerable to adversarial perturbations, cannot be cross-examined in a court of law, and fail to provide the chain-of-custody documentation required by judicial standards (such as the Federal Rules of Evidence 901 and the Daubert standard).

Q-TRACE re-establishes forensic integrity by operating strictly as an **examiner decision-support workstation**. It separates objective physical measurements from subjective human hypotheses, enforces local-first data isolation, and provides mathematically verifiable forensic telemetry.

---

## 2. Related Work & Academic Attribution
Q-TRACE builds upon foundational literature across digital image forensics and quantum information processing:
- **Novel Enhanced Quantum Representation (NEQR):** Zhang et al. (2013) introduced the entanglement of 2D spatial coordinate registers with gray-scale intensity registers, providing an quadratic quantum state storage advantage over FRQI (Le et al., 2011).
- **Quantum Image Arithmetic & Comparators:** Nielsen & Chuang (2010) and Vedral et al. (1996) formalized reversible logic and transverse CNOT-based modular addition/subtraction.
- **Error Level Analysis (ELA):** Krawetz (2007) formalized the analysis of JPEG recompression error rates to detect spliced regions with conflicting compression histories.
- **Sensor Noise Analysis & PRNU:** Lukas et al. (2006) and Mahdian & Saic (2009) established that silicon photo-sensors impart idiosyncratic Photo-Response Non-Uniformity (PRNU) noise patterns, and that local variance inconsistencies reveal digital retouching.
- **Copy-Move Forgery Detection:** Amerini et al. (2011) and Lowe (2004) proved that scale-invariant feature transform (SIFT) descriptors provide robust keypoint matching resilient to scaling and rotation.
- **Content Authenticity Standards:** The Coalition for Content Provenance and Authenticity (C2PA, 2023) established cryptographic manifest standards for media tracking.

---

## 3. Research Gap & Novelty Analysis
As detailed in `docs/RESEARCH_NOVELTY_AND_CONTRIBUTION.md` and `docs/RESEARCH_GAP_ANALYSIS.md`, existing literature leaves three major research gaps:
1. **The Quantum Image Processing Reality Gap:** Theoretical papers propose $O(1)$ quantum image comparisons on megapixel images without disclosing that simulating such states classically requires $281\text{ Terabytes}$ of RAM, or that state preparation requires $O(N)$ classical steps.
2. **The Automotive False-Positive Gap:** Standard ELA produces massive false alarms on specular highlights and metallic car flake paints.
3. **The Courtroom Admissibility Gap:** Academic prototypes lack immutable evidence ledgers, audit logs, and versioned report compilation.

Q-TRACE bridges these gaps through its $4 \times 4$ micro-patch quantum comparator, Coupon Collector sampling derivation, orthogonal consensus fusion, and WORM-emulated local storage engine.

---

## 4. Q-TRACE System Architecture
Q-TRACE is built as a local-first workstation comprising:
- **Backend Core:** FastAPI (Python 3.11.9) with SQLite WAL journal mode, providing ACID transaction guarantees and concurrent read/write isolation.
- **Forensic Pipeline Subsystem:** Modular analyzer architecture (`ForensicTechnique` abstract base class) enforcing non-destructive evidence analysis.
- **Interactive Canvas Engine:** High-performance Canvas2D viewport supporting real-time pan/zoom up to $1000\%$, sub-pixel coordinate alignment, and layer blending.
- **Quantum Laboratory:** Qiskit Aer simulation harness executing 16Q and 12Q circuit graphs on investigator-targeted micro-patches.
- **Dossier & Export Engine:** ReportLab document compilation generating cryptographically sealed multi-page PDFs with running headers and technical appendices.

```
+-------------------------------------------------------------------------------+
|                        Q-TRACE PLATFORM ARCHITECTURE                          |
+-------------------------------------------------------------------------------+
|  React 18 / Vite / TypeScript Workstation UI (Dark Forensic Design System)     |
|    |                                                                          |
|    |-- REST API Endpoints (RFC 7807 Error Envelope Shielding)                 |
|    v                                                                          |
|  FastAPI Backend (Localhost 127.0.0.1)                                        |
|    |                                                                          |
|    |---> Storage Subsystem (WORM Emulation, NTFS Read-Only, SHA-256 Hashing)   |
|    |---> SQLite WAL Database (Case Ledgers, ROIs, Dossiers, Audit Events)     |
|    |---> Classical Forensics Engine (ELA, Noise PRNU, SIFT CMFD, Consensus)  |
|    |---> Quantum Laboratory Engine (16Q / 12Q Qiskit Aer Statevector Engine)  |
|    +---> Reporting & Dossier Engine (Two-Pass ReportLab Multi-Page PDF)       |
+-------------------------------------------------------------------------------+
```

---

## 5. Cryptographic Evidence Ledger & WORM Model
To prevent evidence repudiation in legal proceedings, Q-TRACE implements a software Write-Once-Read-Many (WORM) storage model:
1. Upon upload, the incoming binary stream is processed in $64\text{ KB}$ chunks through hardware-accelerated SHA-256.
2. The file is written to `storage/originals/<sha256>_<sanitized_name>`.
3. The host file system attribute is locked using `stat.S_IREAD` (Windows NTFS read-only flag).
4. Any subsequent attempt to modify or overwrite the physical file is blocked by the operating system. Before every analysis execution, Q-TRACE recalculates the SHA-256 digest against the database record; any detected bit-flip raises an immediate `IntegrityException` and halts the investigation.

---

## 6. Classical Digital Image Forensics Engine
The classical engine executes four orthogonal analytical techniques:
- **Error Level Analysis (ELA):** Recompresses images across controlled quality factors ($Q \in [50, 95]$) and computes edge-masked error residuals.
- **Sensor Noise Inconsistency:** Evaluates spatial noise variance using median filtration and sliding $16 \times 16$ block variance.
- **Keypoint CMFD:** Extracts SIFT feature descriptors, applies Lowe's ratio test, and clusters parallel spatial displacement vectors ($D > 30\text{ px}$).
- **Perceptual Hashing & Color Statistics:** Computes 64-bit aHash, dHash, and pHash fingerprints alongside 256-bin RGB histograms and Shannon entropy.

---

## 7. Multi-Signal Spatial Consensus Fusion
To overcome single-technique vulnerability to false positives on vehicular metallic coatings, Q-TRACE implements spatial Intersection-over-Union (IoU) clustering:
$$\text{IoU}(r_a, r_b) = \frac{\text{Area}(r_a \cap r_b)}{\text{Area}(r_a \cup r_b)}$$
Candidate bounding boxes from independent techniques are merged if $\text{IoU} \ge 0.20$. Merged consensus regions receive a cross-validation score elevation:
$$S_{fused} = \min\left(0.99, \; \frac{1}{|C|} \sum_{r \in C} r.s + 0.15 \times (K - 1)\right)$$
Where $K$ is the number of distinct contributing physical domains. Empirical ablation proves that consensus fusion ($K \ge 2$) reduces false positive pixels to **exactly zero** on authentic vehicle panels.

---

## 8. Quantum Image Representation (NEQR)
Q-TRACE utilizes the Novel Enhanced Quantum Representation (NEQR) to encode $4 \times 4$ image micro-patches:
$$|\Psi\rangle = \frac{1}{4} \sum_{Y=0}^{3} \sum_{X=0}^{3} |YX\rangle \otimes |C_{YX}\rangle$$
Spatial coordinates are mapped to 4 qubits ($|Y_1 Y_0 X_1 X_0\rangle$), while pixel intensities are mapped to 4-bit binary values ($|C_3 C_2 C_1 C_0\rangle$).

---

## 9. 16-Qubit Dedicated Difference Comparator
The 16Q comparator prepares original patch $A$ and modified patch $B$ in superposition, allocating 4 dedicated difference qubits initialized to $|0000\rangle$:
$$|\Phi_0\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |A(k)\rangle_{orig} \otimes |B(k)\rangle_{mod} \otimes |0000\rangle_{diff}$$
A sequence of 8 transverse CNOT gates maps the bitwise XOR directly into the difference register:
$$|\Phi_1\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |A(k)\rangle_{orig} \otimes |B(k)\rangle_{mod} \otimes |A(k) \oplus B(k)\rangle_{diff}$$
Because CNOT is its own inverse, the circuit is strictly unitary and reversible ($U U^\dagger = I_{16}$). Total gate count is 48 gates, circuit depth is 24, and statevector memory is $1.05\text{ MB}$.

---

## 10. 12-Qubit Compact In-Place Comparator
To demonstrate quantum circuit optimization, Q-TRACE introduces a 12-qubit in-place architecture that eliminates the dedicated difference register. By performing the CNOT comparison directly into the target pixel register, the qubit count is reduced by $25\%$, total gate count drops to 36, and classical simulation memory shrinks by $16\times$ ($65.5\text{ KB}$ vs $1.05\text{ MB}$).

---

## 11. Stochastic Measurement & Coupon Collector Theorem
Measurement collapses the quantum state into a single spatial coordinate. Reconstructing the complete difference image requires collecting all 16 coordinates.

We prove mathematically that:
$$E[T] = N \sum_{i=1}^{N} \frac{1}{i} = 16 \sum_{i=1}^{16} \frac{1}{i} \approx \mathbf{54.09\text{ shots}}$$
And by tail bound analysis:
$$P(T > s) \le 16 e^{-s/16} \implies s \ge 16 \ln(16,000) \approx \mathbf{154.9\text{ shots}}$$
Empirical trials confirm that at $S \ge 128$ shots, complete coordinate reconstruction is achieved in $100\%$ of runs, with bitwise exact parity to classical XOR.

---

## 12. Unobserved Coordinate Encoding Protocol (-1)
When shot counts are constrained ($S \le 64$), certain coordinates will remain unobserved. In naive implementations, unobserved pixels default to $0$, falsely signaling authentic matching pixels. Q-TRACE enforces an incomplete readout protocol where unobserved coordinates are strictly encoded as `-1` (unobserved) and visually rendered with distinct diagonal hatching, ensuring scientific honesty.

---

## 13. Experimental Infrastructure & Synthetic Benchmark Suite
All experimental benchmarks are implemented under `experiments/part9/` with raw outputs stored in `results/part9/`. Because confidential insurance claims data cannot be shared, Q-TRACE provides a deterministic synthetic benchmark generator creating metallic vehicle panels with known ground truth masks for splicing, copy-move, and noise smoothing attacks.

---

## 14. Classical Forensic Empirical Results
Evaluated on synthetic vehicular benchmarks, the classical suite achieved:
- **Splicing Detection:** $100\%$ recall, $0.2036$ IoU (enclosing foreign patch).
- **Noise Inconsistency:** $100\%$ recall, $0.1500$ IoU.
- **Authentic Control:** $100\%$ specificity, zero false detections under consensus fusion.
- **Latency:** Average analysis latency was $28.5\text{ ms}$ for ELA, $25.1\text{ ms}$ for Noise, and $22.0\text{ ms}$ for CMFD on $320 \times 320$ patches.

---

## 15. Post-Processing & JPEG Quality Robustness
Subjecting spliced vehicle panels to JPEG recompression sweeps ($Q \in \{50, 70, 85, 95\}$) revealed:
- Full retention of foreign compression differentials down to $Q=70$ ($100\%$ spatial recall).
- Complete residual loss at $Q \le 50$, where coarse global quantization overrides pre-existing compression histories. Q-TRACE automatically flags low-quality inputs with a limitation warning.

---

## 16. Quantum Empirical Results & Timing Breakdown
High-resolution microsecond timing benchmarks on a $4 \times 4$ patch revealed:
- **Classical XOR Difference:** **$76.01\ \mu\text{s}$**
- **16Q Quantum Total Pipeline:** **$100.66\text{ ms}$** (Circuit build: $2.88\text{ ms}$; Aer simulation: $97.66\text{ ms}$; Reconstruction: $0.12\text{ ms}$)
- **Speed Advantage Ratio:** Classical is **$1,324.3\times$ faster** than classical simulation of the quantum circuit.

---

## 17. Forensic Fusion Ablation Study
Ablating 9 configurations across 4 attack modalities revealed that while single-technique ELA produced 1,024 false positive pixels on authentic panel body seams, **Pairwise Consensus ($K \ge 2$) and Full Ensemble Consensus eliminated false positive pixels entirely (0 FP pixels)** while preserving high-confidence detection.

---

## 18. System Performance & Resolution Scaling
Throughput benchmarks demonstrated excellent performance across resolutions:
- $256 \times 256$: $78.66\text{ ms}$ total forensic runtime.
- $512 \times 512$: $150.95\text{ ms}$ total forensic runtime.
- $1024 \times 1024$: $538.97\text{ ms}$ total forensic runtime.
- $1920 \times 1080$ (Full HD): $1,378.37\text{ ms}$ ($1.38\text{s}$) total forensic runtime.
- **PDF Report Generation:** Compiled multi-page courtroom dossiers in **$93.68\text{ ms}$** ($8.82\text{ KB}$).

---

## 19. Security Hardening & Threat Modeling
Automated security testing (`tests/test_security_hardening.py`) verified 100% defense against:
1. Path traversal attacks (`../../etc/passwd`, null bytes).
2. Magic byte spoofing (disguised executables, bash scripts, and SVG XSS).
3. Decompression bombs (memory threshold ceilings).
4. Physical disk bitstream tampering (WORM SHA-256 detection).

---

## 20. Usability & Human-in-the-Loop Investigation Workflow
A structured 10-step usability walkthrough confirmed that examiners can ingest evidence, verify integrity, inspect candidate anomalies on Canvas2D, run quantum experiments, record contextual hypotheses, and export signed PDFs with low cognitive load and zero UI freezing.

---

## 21. Research Limitations & Future Directions
Q-TRACE identifies four primary research boundaries:
1. Quantum execution is restricted to simulation of $4 \times 4$ micro-patches; real QPU dispatch requires error-corrected hardware.
2. Extremely aggressive global recompression ($Q < 50$) destroys high-frequency ELA differentials.
3. Optical WORM storage is emulated via software NTFS permissions and SHA-256 checks rather than write-once optical media.
4. Final fraud determinations require human examiner corroboration with physical repair shop work orders.

Future work will explore OpenQASM compilation for cloud QPU backends, automated deep learning in-painting detection, and distributed blockchain evidence notarization.

---

## 22. Conclusion & Academic Verdict
Q-TRACE successfully demonstrates that digital image forensics can achieve scientific rigor, cryptographic integrity, and transparency without relying on opaque predictive scoring. The platform establishes an academically defensible foundation for quantum-assisted digital investigation.

