# Q-TRACE — Project Overview & Executive Research Summary

**Document ID:** `DOC-KB-001`  
**Classification:** Research, Feasibility & System Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Course Context:** University Undergraduate B.Tech Capstone / Quantum Mechanics & Quantum Computing Coursework  

---

## 1. Executive Summary

Digital photographs have become the primary evidentiary substrate for high-stakes administrative, financial, and legal determinations—most notably in **motor insurance claim assessments**. Every year, millions of insurance claims worldwide rely on smartphone photographs of damaged vehicles to estimate claim payouts, authorize repair work, or write off losses. Concurrently, accessible digital photo-editing software, generative image fill, and AI-driven manipulation tools have lowered the technical barrier for malicious tampering to near zero. 

A claimant can easily:
1. Artificially splice severe bodywork denting or broken glass onto an otherwise pristine vehicle panel.
2. Clone a scratch or structural fracture from one damaged panel to another (copy-move forgery).
3. Digitally inpaint or erase pre-existing structural wear or unrelated vehicular damage before claiming against a recent minor collision.
4. Duplicate photographic damage across distinct claims (repeat billing).
5. Modify or strip EXIF timestamps and geolocation coordinates to fabricate temporal consistency with an accident report.

Traditional human visual review consistently fails to detect subtle, boundary-blended, or re-compressed digital modifications. On the other hand, purely automated "black-box" artificial intelligence classifiers often suffer from severe unreliability: they output uncalibrated fraud scores without explainable spatial evidence, produce catastrophic false positives on natural lighting gradients, and are legally inadmissible because they cannot maintain a cryptographic **Chain of Custody**.

**Q-TRACE (Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform)** is engineered to solve this crisis. 

Q-TRACE is a dual-engine digital forensics workstation designed for insurance investigators, forensic examiners, and university research reviewers. It unites:
- **A Multi-Method Classical Forensics Engine:** Implementing complementary, physics- and signal-based tampering detection algorithms (Error Level Analysis, SIFT/ORB keypoint copy-move localization, wavelet/median noise residual inconsistency, edge-blending gradient delta, and EXIF metadata structural parsing).
- **An Experimental Quantum Image Processing (QIP) Laboratory:** A mathematically rigorous quantum simulation environment implementing Novel Enhanced Quantum Representation (NEQR)-inspired quantum circuits. It demonstrates coherent spatial superposition, multi-register bitwise quantum XOR pixel comparison, state collapse sampling, and Grover-accelerated global anomaly detection on high-priority suspicious image patches.
- **An Evidence-First Interactive Investigation Canvas:** A dark-laboratory workstation interface centered around high-precision image navigation, multi-layer heatmap overlays, bounding-box Region-of-Interest (RoI) consensus inspection, and a cryptographic forensic timeline.
- **Cryptographic File Preservation & Traceable Reporting:** Enforcing strict Write-Once-Read-Many (WORM) evidence storage, SHA-256 byte-level verification manifests, and deterministic, auditable PDF forensic dossiers.

---

## 2. Mission & Core Problem Statement

### 2.1 Formal Problem Statement

> **How can we engineer a digital image-forensics platform that ingests suspicious digital photographs, preserves cryptographic file integrity, identifies and localizes indicators of physical and digital manipulation across multiple independent signal domains, provides explainable visual and numerical evidence for human decision-support, and evaluates classical versus quantum image-processing paradigms in an open, reproducible experimental environment?**

### 2.2 System Boundary & Ethical Mandate

A fundamental principle governing Q-TRACE is that **it is an investigative decision-support system, not an automated judicial tribunal.**

```
+-----------------------------------------------------------------------------------------+
|                                    Q-TRACE BOUNDARY                                     |
|                                                                                         |
|  [ Ingested Image ] ---> [ Cryptographic Hashing ] ---> [ Independent Analysis Modules ] |
|                                                                 |                       |
|                                                                 v                       |
|  [ Traceable Report ] <--- [ Evidence Fusion Canvas ] <--- [ Physical & Signal Anomalies] |
+-----------------------------------------------------------------------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   HUMAN FORENSIC EXAMINER     |
                         |  (Evaluates Context, Policy,   |
                         |   Physical Feasibility, Law)  |
                         +-------------------------------+
                                         |
                                         v
                            [ Legal / Claims Decision ]
```

- **Observed Physical Evidence vs. Legal Conclusions:** The system flags physical and statistical inconsistencies—such as mismatched JPEG quantization tables, high-frequency noise variance between panels, duplicated keypoint feature clusters, or quantum register bit discrepancies. The system **never** outputs statements such as *"The claimant is guilty of fraud."*
- **Explainability:** Every suspicious region flagged by the platform must be directly attributable to one or more deterministic signal analyses. An examiner must be able to inspect the exact mathematical and visual justification behind every highlighted pixel.
- **Original Evidence Inviolability:** Ingested files are immediately hashed (SHA-256) and preserved in a read-only vault. All forensic pipelines execute exclusively on memory buffers or documented working derivatives.

---

## 3. Primary Real-World Application: Motor Insurance Claims

While designed with an extensible modular core capable of supporting document analysis, satellite change detection, and forensic journalism, the primary operational focus of Q-TRACE is **motor vehicle insurance claim photographic fraud**.

### 3.1 Realistic Threat Models & Detectability

| Scenario ID | Attack Vector | Real-World Operational Example | Forensic Detection Mechanism in Q-TRACE | Detectability Rating |
| :--- | :--- | :--- | :--- | :--- |
| **SC-01** | **Digital Damage Insertion (Splicing)** | Claimant downloads an image of a crumpled fender or smashed headlight from the internet and blends it into a photo of their intact vehicle. | **Noise Inconsistency & Error Level Analysis (ELA):** The spliced patch exhibits a foreign noise floor (different ISO/sensor profile) and a divergent JPEG compression history compared to the host bodywork. | **High** (if uncompressed or moderately compressed); **Medium** (if heavily degraded). |
| **SC-02** | **Damage Duplication (Copy-Move)** | Claimant takes a genuine small scratch on the door panel and duplicates it multiple times across the quarter-panel and rear bumper to inflate repair cost. | **SIFT/ORB Keypoint Matching + Spatial Clustering:** Identifies identical feature descriptor sets occurring in distinct spatial coordinates across the same vehicle. | **Very High** (robust against scaling, small rotations, and local brightness shifts). |
| **SC-03** | **Pre-Existing Wear Removal (Inpainting)** | Vehicle has pre-existing rust or a historical dent. Claimant digitally erases it prior to an accident claim, or erases non-accident damage during post-repair inspection. | **Gradient Discontinuity & High-Frequency Residuals:** Inpainting fills pixels using smooth interpolations or generative textures, leaving distinct boundary gradient drops and zero-noise "dead zones." | **Medium** (requires high-resolution inspection and edge-variance profiling). |
| **SC-04** | **Re-used Incident Imagery (Metadata Fraud)** | Claimant submits a genuine crash photo from three years prior as a newly occurred accident. | **EXIF Structure & Metadata Verification:** Dissects internal camera metadata, hardware serial hashes, software modification flags, thumbnail discrepancies, and GPS/timestamp consistency. | **High** (if EXIF intact); **Defeated if metadata stripped** (triggers metadata-absence warning). |
| **SC-05** | **Pre-loss vs. Post-loss Image Comparison** | Insurer provides an original reference photo (e.g., policy inception inspection) and the claimant submits a post-accident photo taken from the same vantage point. | **Reference Difference Mapping & Quantum Patch Comparison:** Coherent pixel-level intensity subtraction, structural similarity (SSIM) delta, and experimental quantum bitwise XOR verification. | **Very High** (exact geometric alignment yields absolute discrepancy bounds). |

---

## 4. The Dual-Engine Paradigm: Classical Forensics + Quantum Laboratory

A distinguishing hallmark of Q-TRACE is its dual-engine architecture. It rejects the false dichotomy of "purely classical" versus "fictitious quantum supremacy." Instead, each engine serves a clear, defensible purpose:

```
                                +-----------------------------------+
                                |     INGESTED EVIDENCE IMAGE       |
                                +-----------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
        +----------------------------------+             +----------------------------------+
        |   CLASSICAL FORENSICS ENGINE     |             |    QUANTUM PROCESSING LAB        |
        |  (Full-Scale Production Core)    |             |  (Patch-Level Deep Verification) |
        +----------------------------------+             +----------------------------------+
        | - Error Level Analysis (ELA)     |             | - Focus on High-Suspicion Patches|
        | - SIFT/ORB Copy-Move Engine      |             | - NEQR State Superposition       |
        | - Wavelet Noise Discrepancy      |             | - Coherent Multi-Register XOR    |
        | - Boundary Gradient Variance     |             | - State Collapse & Sampling      |
        | - EXIF & Structural Parsing      |             | - Grover Discrepancy Search      |
        +----------------------------------+             +----------------------------------+
                         |                                                 |
                         +------------------------+------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                |     INTELLIGENCE EVIDENCE FUSION  |
                                |  (Consensus Scoring & Heatmaps)   |
                                +-----------------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                |    EVIDENCE CANVAS WORKSTATION    |
                                |  (Interactive Human Investigation)|
                                +-----------------------------------+
```

1. **The Classical Engine provides real-world production utility:** It operates instantaneously across full-resolution multi-megapixel photographs, scanning the entire canvas for physical and statistical anomalies.
2. **The Quantum Laboratory provides an academically rigorous experimental testbed:** Real-world quantum computing in the NISQ (Noisy Intermediate-Scale Quantum) era cannot encode a 12-megapixel photograph (which would require millions of error-corrected qubits). However, by utilizing **Forensic Patch Tiling**, suspicious $4 \times 4$ or $8 \times 8$ regions flagged by the classical engine can be ingested into the quantum simulator. Here, students, researchers, and examiners can inspect quantum state superposition, track unitary gate evolution, analyze measurement collapse statistics, and experimentally benchmark quantum versus classical algorithmic scaling.

---

## 5. Five Pillars of the Q-TRACE Workstation

1. **Pillar 1: Cryptographic Integrity & Chain of Custody**
   - Immediate generation of SHA-256 digests upon ingestion.
   - Immutable evidence manifests storing original file names, MIME types, byte sizes, timestamps, and hashes.
   - WORM (Write-Once-Read-Many) evidence storage architecture preventing in-place mutations.

2. **Pillar 2: Classical Multi-Signal Forensic Arsenal**
   - Orthogonal forensic modalities covering compression artifacts, spatial repetition, high-frequency noise variance, edge blending, and metadata.
   - Elimination of single-point-of-failure heuristic flags.

3. **Pillar 3: NEQR-Based Quantum Verification Laboratory**
   - Fully mathematically validated 16-qubit (and alternative 12-qubit in-place) quantum image comparison circuits.
   - Realistic simulation of state preparation, quantum registers (position, reference intensity, test intensity, difference), unitary CNOT transformations, and measurement collapse dynamics.
   - Direct integration with IBM Qiskit and Qiskit Aer simulation runtimes.

4. **Pillar 4: Evidence Canvas & Region Inspector Interface**
   - High-performance, distraction-free visual environment designed around an industrial "Dark Laboratory" design aesthetic (graphite/midnight surfaces, electric cyan, quantum violet, and amber alert signals).
   - Smooth pan, zoom, split-screen swipe comparison, layer opacity blending, and click-to-inspect Region-of-Interest (RoI) inspector drawers.

5. **Pillar 5: Reproducible Case Dossiers & PDF Generation**
   - Structured SQLite case database recording every parameter, version, execution timestamp, and examiner annotation.
   - Deterministic, tamper-evident PDF generation with embedded SHA-256 evidence verification blocks suitable for university evaluation or real-world insurance claim documentation.

---

## 6. University Course & Viva Alignment

This project is tailored specifically to excel in a rigorous university computer science and quantum computing academic defense:

- **Mathematical Depth:** The student can stand at the whiteboard and derive the exact tensor products of the composite Hilbert space $|\Psi\rangle = |f_A\rangle \otimes |f_B\rangle \otimes |D\rangle \otimes |Y\rangle \otimes |X\rangle$, explain the unitary decomposition of multi-controlled NOT gates, calculate probability amplitudes, and derive the Coupon Collector sampling bounds.
- **Scientific Honesty:** Q-TRACE candidly addresses the fundamental bottlenecks of quantum image processing (state preparation complexity, measurement sampling overhead, and simulator memory limits) rather than claiming fictitious "quantum supremacy."
- **Practical Engineering:** Q-TRACE is a fully functional, local, modern software product built with enterprise-grade engineering practices—comprehensive test suites, clear API contracts, strict typing, and reproducible configuration.

---

*Continue to `RESEARCH_INDEX.md` for document navigation and `LITERATURE_REVIEW.md` for the comprehensive academic survey.*

