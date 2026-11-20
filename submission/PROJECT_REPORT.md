# Q-TRACE: Final Capstone Academic Project Report
## Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform

**Author / Developer:** Pranav Agarwal  
**Repository:** `https://github.com/agarwalpranav0711/quantum-qtrace`  
**Version:** 1.0.0 Production Release  
**Domain:** Digital Media Forensics, Quantum Information Science, Software Engineering  

---

### Abstract
Digital image manipulation in automobile insurance claims represents a growing financial and legal liability. While classical forensic techniques (such as Error Level Analysis and sensor noise modeling) are widely studied, their operational integration into local-first, court-defensible investigative workflows remains fragmented. Furthermore, the geometric sensitivity of quantum state spaces for sub-pixel image micro-texture comparison has not been systematically explored in forensic software. 

This work presents **Q-TRACE**, a 100% local-first, air-gapped capable digital image forensics workstation. Q-TRACE integrates a Write-Once, Read-Many (WORM) evidence vault with SHA-256 cryptographic sealing, a six-technique classical forensics analysis engine, a dual-viewport synchronized Canvas2D comparison environment, an experimental Qiskit-powered quantum state micro-patch simulator, and an automated ReportLab multi-page courtroom dossier generator. On a benchmark of 120 synthetic vehicle claim tampering cases, the composite classical engine achieved an aggregate F1-score of $0.878$ (AUC-ROC $0.932$), while the quantum state fidelity metric demonstrated $+65.0\%$ higher dynamic sensitivity to subtle edge discontinuities than standard Euclidean distance. Crucially, Q-TRACE enforces an evidentiary decision-support boundary, refuting automated fraud declarations and operating without reliance on cloud infrastructure.

---

### 1. Introduction & Motivation
Motor vehicle insurance fraud accounts for billions of dollars in annual losses worldwide. With the ubiquity of high-resolution smartphone cameras and accessible desktop editing tools (Photoshop, GIMP) and generative AI inpainting, claimants can duplicate collision damage, composite damage from foreign vehicles, or erase pre-existing structural flaws.

Forensic examination of these images faces several acute challenges:
1. **Chain-of-Custody Integrity:** Digital images must be verifiably preserved against tampering or accidental modification during analysis.
2. **Lossy Compression Artifacts:** Multi-pass transmission through messaging apps destroys delicate statistical fingerprints.
3. **Lack of Integrated Examiner Tools:** Examiners are forced to switch between disconnected scripts, command-line utilities, and general-purpose image editors.
4. **Cloud Privacy Risks:** Uploading confidential claim photos containing license plates, vehicle identification numbers (VIN), and residential locations to third-party cloud servers violates privacy and compliance standards.

Q-TRACE addresses these challenges through a unified, offline, local-first engineering architecture.

---

### 2. System Architecture & Methodology

#### 2.1 Evidence Vault & WORM Ingestion
Every image uploaded to Q-TRACE is intercepted before decoding. Physical magic bytes (`FF D8 FF`, `89 50 4E 47`, etc.) are audited to prevent polyglot exploits, decompression limits are enforced ($100\text{ MP}$), and a SHA-256 digest is generated. The master image is written to immutable storage (`storage/originals/{uuid}.ext`) under a strict Write-Once, Read-Many (WORM) contract.

#### 2.2 Classical Forensic Filter Suite
1. **Error Level Analysis (ELA):** Detects non-uniform DCT quantization error residuals across JPEG qualities $95, 90, 85$.
2. **Local Noise Variance:** Measures Laplacian high-pass standard deviation across $32 \times 32$ spatial tiles to flag foreign sensor noise.
3. **Copy-Move Detection:** Identifies duplicated image regions using SIFT and ORB descriptors clustered with spatial Euclidean distance thresholds ($\Delta s > 40\text{ px}$).
4. **CFA Bayer Pattern Demosaicing:** Analyzes periodic interpolation artifacts in chromatic residual spectra.
5. **Metadata Verification:** Audits EXIF timestamps, camera make/model, and editing software signatures.
6. **Perceptual Hashing:** Generates 64-bit structural fingerprints (pHash, aHash, dHash) for fast derivative search.

#### 2.3 Interactive Forensic Canvas
Implemented using HTML5 Canvas2D and React 19, the forensic canvas features dual-viewport synchronized pan and zoom (up to 3200%), split-screen interactive curtain wipes, pixel difference/exclusion blending modes, polygon ROI drawing, and examiner note binding.

#### 2.4 Quantum-Assisted Micro-Patch Simulation
Q-TRACE investigates the representational properties of quantum state spaces for micro-patch texture verification:
- Normalized pixel intensities of $4 \times 4$ ($16$ amplitudes) and $8 \times 8$ ($64$ amplitudes) micro-patches are encoded into statevectors $|\psi\rangle = \sum c_i |i\rangle$ via amplitude encoding.
- Projective measurement statistics are gathered using the Qiskit Aer statevector simulator.
- Quantum distance is evaluated via Uhlmann Quantum Fidelity ($F$) and Quantum Trace Distance ($D$).
- Shot sufficiency is mathematically governed by the Coupon Collector's theorem:
  $$\mathbb{E}[T] = N \cdot H_N \approx 54.08 \text{ shots for } N=16 \ll 2048 \text{ shots used}$$

#### 2.5 Automated Dossier Compiler
Using ReportLab, Q-TRACE synthesizes case metadata, SHA-256 verification ledgers, examiner notes, high-resolution forensic heatmaps, and quantum experiment charts into an official multi-page PDF dossier.

---

### 3. Empirical Results & Discussion

#### 3.1 Detection Performance (120 Synthetic Testbed)
- **Copy-Move:** Precision $93.3\%$, Recall $93.3\%$, F1 $0.933$
- **Splicing:** Precision $90.0\%$, Recall $90.0\%$, F1 $0.900$
- **Object Removal:** Precision $86.2\%$, Recall $83.3\%$, F1 $0.847$
- **Enhancement:** Precision $83.3\%$, Recall $83.3\%$, F1 $0.833$
- **Composite Ensemble:** **Precision 88.2%, Recall 87.5%, F1 0.878, AUC-ROC 0.932**

#### 3.2 Quantum Metric Sensitivity
On 250 micro-patch pairs, Quantum Fidelity demonstrated a dynamic separation $\Delta = 0.1274$ between pristine and tampered textures, representing a $+65.0\%$ higher sensitivity to high-frequency edge shifts compared to classical cosine similarity ($\Delta = 0.0772$).

---

### 4. Candid Scientific Boundaries & Limitations
1. **Decision-Support Boundary:** Q-TRACE does not declare guilt or fraud. Non-uniformities can arise legitimately from OEM HDR processing, dirt, or social media compression.
2. **No Quantum Algorithmic Speedup:** Simulations run classically on CPU. The contribution is representational sensitivity, not runtime speedup.
3. **Compression Floor:** High-frequency noise filters degrade significantly at $Q < 50$.

---

### 5. Conclusion & Future Outlook
Q-TRACE provides a complete, robust, local-first digital forensics workstation bridging classical signal processing and quantum state simulation. Future work will extend the platform toward hardware QPU execution and Vision Transformer (ViT) deep feature embeddings.

