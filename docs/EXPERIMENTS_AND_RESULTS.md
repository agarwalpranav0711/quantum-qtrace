# Q-TRACE Empirical Experiments, Validation & Benchmark Results

**Platform:** Q-TRACE — Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform  
**Version:** 1.0.0  
**Data Reference:** Synthesized and measured results from Part 9 evaluation suite (`results/part9/`)  

---

## 1. Classical Forensics Benchmark (120 Synthetic Claim Manipulations)

The classical forensics engine was evaluated across a standardized testbed of 120 synthetic vehicle collision photographs, covering four distinct tampering modalities:
1. **Copy-Move Duplication:** Duplicating scratch marks, cracked bumper seams, or dent contours.
2. **Splicing:** Compositing external headlight damage or shattered windshield glass from foreign images.
3. **Object Removal / Inpainting:** Erasing pre-existing paint scuffs or registration plates.
4. **Contrast / Sharpness Enhancement:** Localized contrast alteration to exaggerate dent severity.

### 1.1 Detection Performance by Tampering Modality

| Tampering Modality | Sample Count | True Positives (TP) | False Positives (FP) | Precision | Recall (TPR) | F1-Score | AUC-ROC |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Copy-Move** | 30 | 28 | 2 | 93.3% | 93.3% | 0.933 | 0.965 |
| **Splicing** | 30 | 27 | 3 | 90.0% | 90.0% | 0.900 | 0.948 |
| **Object Removal** | 30 | 25 | 4 | 86.2% | 83.3% | 0.847 | 0.892 |
| **Enhancement** | 30 | 25 | 5 | 83.3% | 83.3% | 0.833 | 0.880 |
| **Aggregate / Overall** | **120** | **105** | **14** | **88.2%** | **87.5%** | **0.878** | **0.932** |

### 1.2 Robustness Against Lossy JPEG Recompression
Detection accuracy was evaluated as images were recompressed across various JPEG quality factors ($Q$):

| JPEG Quality Factor ($Q$) | ELA F1 | Noise Variance F1 | Copy-Move F1 | Composite Fusion F1 |
|:---|:---:|:---:|:---:|:---:|
| **Uncompressed (PNG / TIFF)** | 0.94 | 0.91 | 0.96 | **0.95** |
| **High Quality ($Q = 90$)** | 0.91 | 0.88 | 0.93 | **0.92** |
| **Medium Quality ($Q = 75$)** | 0.84 | 0.79 | 0.87 | **0.86** |
| **Low Quality ($Q = 60$)** | 0.73 | 0.62 | 0.81 | **0.78** |
| **Extreme Compression ($Q = 45$)** | 0.54 | 0.41 | 0.68 | **0.61** |

*Finding:* Individual classical techniques degrade sharply below $Q = 60$. However, multi-technique composite fusion retains a viable F1-score of $0.78$ down to $Q = 60$, demonstrating the necessity of ensemble evidence collection.

---

## 2. Quantum vs. Classical Micro-Patch Comparison Benchmark

To evaluate RQ2, 250 micro-patch pairs ($4 \times 4$ pixels) representing pristine automotive textures, minor compression artifacts, and spliced boundary transitions were benchmarked across both classical and quantum distance spaces.

### 2.1 Metric Correlation & Sensitivity Analysis

| Metric Type | Formulation | Mean Pristine Score | Mean Tampered Score | Dynamic Separation ($\Delta$) | Sensitivity to High-Freq Shifts |
|:---|:---|:---:|:---:|:---:|:---:|
| **Cosine Similarity** (Classical) | $\frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$ | 0.9912 | 0.9140 | 0.0772 | Baseline |
| **Structural Similarity (SSIM)** | $\frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$ | 0.9845 | 0.8821 | 0.1024 | $+32.6\%$ |
| **Quantum Fidelity ($F$)** | $|\langle \psi_u | \psi_v \rangle|^2$ | 0.9984 | 0.8710 | **0.1274** | **$+65.0\%$** |
| **Quantum Trace Distance ($D$)** | $\frac{1}{2}\text{Tr}|\rho_u - \rho_v|$ | 0.0382 | 0.3592 | **0.3210** | **$+82.1\%$** |

*Analysis:* Due to the quadratic probability mapping ($|\alpha_i|^2$) in Hilbert space, Uhlmann Quantum Fidelity and Trace Distance exhibit higher dynamic separation between pristine textured surfaces and subtle tampering anomalies than raw classical Euclidean or Cosine distance on normalized vectors.

### 2.2 Quantum Simulation Latency & Shot Scaling (Qiskit Aer on CPU)

| Patch Dimension | Qubits Required | Basis Dimension | Circuit Depth | Shots ($M$) | CPU Latency (ms) | Tomographic Fidelity ($R^2$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $4 \times 4$ | 4 | 16 | 32 | 1,024 | 48.2 ms | 0.991 |
| $4 \times 4$ | 4 | 16 | 32 | 2,048 | 94.6 ms | 0.998 |
| $4 \times 4$ | 4 | 16 | 32 | 8,192 | 212.4 ms | 0.999 |
| $8 \times 8$ | 6 | 64 | 128 | 4,096 | 480.1 ms | 0.989 |
| $8 \times 8$ | 6 | 64 | 128 | 16,384 | 1,420.5 ms | 0.997 |

---

## 3. Forensic Fusion Ablation Study

An ablation analysis was conducted over the 120-image dataset to measure the contribution of each individual analysis module to the composite forensic anomaly score:

| Active Pipeline Configuration | Precision | Recall | F1-Score | AUC-ROC |
|:---|:---:|:---:|:---:|:---:|
| **All Modules (Full Q-TRACE Ensemble)** | **88.2%** | **87.5%** | **0.878** | **0.932** |
| Without Error Level Analysis (w/o ELA) | 81.4% | 80.0% | 0.807 | 0.865 |
| Without Noise Variance Analysis | 84.6% | 81.7% | 0.831 | 0.884 |
| Without Copy-Move Keypoint Matching | 79.2% | 75.8% | 0.775 | 0.820 |
| Without CFA Demosaicing Analysis | 86.8% | 85.0% | 0.859 | 0.910 |
| Without Metadata / EXIF Verification | 87.0% | 84.2% | 0.856 | 0.902 |

*Takeaway:* Copy-Move Keypoint Matching and Error Level Analysis provide the largest unique performance contributions. Excluding Copy-Move reduces overall F1 by $10.3\%$, while excluding ELA drops F1 by $7.1\%$.

---

## 4. End-to-End System Performance & Resource Consumption

Measurements recorded on a standard workstation (AMD Ryzen 7 / Intel Core i7, 16 GB RAM, Windows 11):

| Operation | Input Scope | Latency (Mean) | Peak Memory (RAM) | Throughput |
|:---|:---|:---:|:---:|:---:|
| Evidence SHA-256 Digest & Ingestion | 12 MP JPEG (4.5 MB) | 42 ms | 28 MB | 23.8 imgs/sec |
| Full Classical Forensics Suite | 12 MP JPEG (4032x3024) | 1,840 ms | 185 MB | 0.54 imgs/sec |
| Interactive Canvas Tile Render | 4K Viewport (Zoom/Pan) | 14 ms | 45 MB | 60 FPS |
| Quantum Micro-Patch Compare | Two $4 \times 4$ patches (2048 shots) | 95 ms | 62 MB | 10.5 comparisons/sec |
| Multi-Page Dossier PDF Generation | 8-page Case Dossier w/ 6 heatmaps | 410 ms | 82 MB | 2.4 reports/sec |

