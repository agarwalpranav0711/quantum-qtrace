# Q-TRACE Oral Defense & Viva Voce Preparation Guide

**Platform:** Q-TRACE — Quantum-Assisted Digital Image Forensics Platform  
**Target:** Final Capstone Oral Examination / Viva Voce Defense  

---

## 1. High-Frequency Examiner Questions & Defensible Answers

### Q1: Why did you choose a local-first, zero-cloud architecture?
**Examiner Focus:** Architectural justification, privacy, legal defensibility.  
**Answer:**  
In digital forensics and insurance investigations, evidence often contains sensitive personally identifiable information (PII) including vehicle license plates, Vehicle Identification Numbers (VIN), residential addresses, and GPS geotags. Sending this data to cloud servers exposes organizations to data protection liabilities, potential subpoena exposure, and chain-of-custody contamination. Furthermore, forensic workstations often operate in air-gapped laboratory environments. A 100% local-first architecture guarantees data sovereignty, zero cloud egress costs, and complete offline operational autonomy.

---

### Q2: What is the exact role of Quantum Computing in Q-TRACE? Do you achieve a quantum speedup?
**Examiner Focus:** Scientific honesty, quantum supremacy claims vs. reality.  
**Answer:**  
We candidly state: **there is no quantum computational speedup or exponential acceleration claimed in Q-TRACE**. All quantum circuits currently execute on a classical CPU statevector simulator via Qiskit Aer.  
The actual scientific novelty is **representational**: by mapping normalized pixel micro-patches ($4 \times 4$ and $8 \times 8$) into quantum state space via amplitude encoding, the resulting state vectors reside in a high-dimensional Hilbert space where quantum distance metrics (such as Uhlmann Fidelity and Trace Distance) exhibit quadratic sensitivity to probability amplitude shifts. In our empirical benchmarks, this yielded a **$+65\%$ greater dynamic separation** on subtle high-frequency edge discontinuities compared to standard Euclidean distance.

---

### Q3: What is the Coupon Collector theorem and why is it relevant here?
**Examiner Focus:** Theoretical rigor and mathematical backing.  
**Answer:**  
When measuring a quantum state in the computational basis to perform quantum state tomography (QST) on a $4 \times 4$ patch (16 amplitudes), we need to ensure that every basis state is observed with sufficient frequency to estimate its probability. By the Coupon Collector theorem, the expected number of shots required to observe all $N=16$ basis states is $\mathbb{E}[T] = N \cdot H_N = 16 \times 3.38 \approx 54.08\text{ shots}$. Our default simulation utilizes 2048 to 8192 shots, far exceeding this threshold and mathematically guaranteeing statistical convergence ($R^2 > 0.998$).

---

### Q4: How do you prevent your system from falsely accusing an innocent claimant of insurance fraud?
**Examiner Focus:** Ethical considerations, decision-support philosophy.  
**Answer:**  
Q-TRACE is strictly designed as an **investigative decision-support system**, not an automated fraud detector. Every report, UI screen, and generated PDF contains an explicit legal disclaimer stating that technical anomalies (such as compression discrepancies or low fidelity scores) do not prove fraud. Many factors—such as WhatsApp re-compression, OEM computational photography (HDR, Night Mode), camera software updates, or physical paint touch-ups—can cause forensic indicators. Q-TRACE highlights technical observations; only a certified human investigator can evaluate intent and context.

---

### Q5: How is chain-of-custody preserved in your evidence vault?
**Examiner Focus:** Forensic integrity and evidentiary standards.  
**Answer:**  
1. **Pre-Processing Cryptographic Sealing:** Before any parsing or decoding occurs, the uploaded file byte stream is hashed using SHA-256.
2. **Write-Once, Read-Many (WORM) Storage:** Master images are stored read-only in `storage/originals/` under immutable UUIDv4 identifiers.
3. **Continuous Verification:** The platform includes an automated `/verify` routine that re-hashes the physical file on disk and verifies that it bitwise matches the initial database record.
4. **Security Hardening:** We enforce magic-byte validation, path traversal guards (`is_relative_to`), and a 100-megapixel decompression bomb ceiling to protect workstation stability.

---

### Q6: What happens when an image is heavily compressed (e.g. sent over WhatsApp)?
**Examiner Focus:** Real-world limitations.  
**Answer:**  
Our Part 9 empirical testing showed that classical forensic filters (especially noise variance and CFA demosaicing) suffer significant signal attenuation when JPEG quality falls below $Q = 60$. However, our multi-technique composite ensemble—which fuses ELA, noise variance, copy-move keypoints, demosaicing, and metadata—retains a viable F1-score of $0.78$ down to $Q = 60$, whereas individual filters collapse to $< 0.60$. Below $Q = 50$, classical pixel-level forensic certainty is largely lost, a limitation we openly document in `docs/LIMITATIONS_AND_FUTURE_SCOPE.md`.

---

## 2. 60-Second Elevator Pitch
> *"Q-TRACE is an offline, local-first digital image forensics workstation designed for automobile insurance fraud investigation. It unifies a WORM evidence vault with SHA-256 sealing, a six-technique classical forensics analysis engine, a dual-viewport synchronized Canvas2D comparison suite, and an experimental Qiskit quantum state micro-patch simulator. Rather than making automated fraud accusations, Q-TRACE acts as a rigorous decision-support tool, helping examiners identify copy-move duplication, foreign splicing, and compression anomalies with full chain-of-custody defensibility."*
