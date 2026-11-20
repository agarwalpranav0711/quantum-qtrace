# Q-TRACE User Guide & Investigation Manual

**Platform:** Q-TRACE — Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform  
**Version:** 1.0.0 (Production Release)  
**Target Audience:** Digital Forensic Investigators, Motor-Vehicle Insurance Special Investigation Units (SIU), Forensic Analysts, Academic Researchers  

---

## 1. Introduction & Investigative Philosophy

Q-TRACE is an offline, local-first digital image forensics workstation designed to assist forensic examiners in analyzing motor-vehicle insurance claim imagery. 

### Core Operating Principles
1. **Decision-Support Architecture:** Q-TRACE does not make automated legal or fraud determinations. Every analytical visualizer, quantum simulation metric, and statistical anomaly is an investigative indicator that must be corroborated by a human expert.
2. **Strict Chain-of-Custody:** Evidence ingested into Q-TRACE is sealed with a cryptographic SHA-256 digest at the exact instant of ingestion. Raw master files are stored read-only (WORM - Write Once, Read Many).
3. **Reproducibility:** Every classical forensic filter and quantum circuit experiment operates with recorded deterministic parameters.

---

## 2. Navigating the Investigation Workstation

The Q-TRACE user interface is organized into five primary functional studios accessible via the global sidebar navigation:

```
[Q-TRACE Navigation]
 ├── 1. Command Center / Case Management
 ├── 2. Evidence Ingestion & Vault
 ├── 3. Classical Forensics Lab
 ├── 4. Interactive Forensic Canvas (ROI & Comparison)
 ├── 5. Quantum Experimentation Lab
 └── 6. Dossier Studio & Executive Reporting
```

---

## 3. Step-by-Step Investigative Workflow

### Stage 1: Creating an Investigation Case
1. Navigate to the **Command Center** (`/`).
2. Click **Create New Case** (`Alt + N`).
3. Fill in the case profile:
   - **Case Title / Number:** e.g., `CASE-2025-0842-AUTO`
   - **Investigator Name / Badge ID:** e.g., `Senior Examiner J. Miller (#4821)`
   - **Claim Reference:** e.g., `CLM-991204-USAA`
   - **Incident Date & Location Description:** Brief context on the alleged collision.
4. Click **Initialize Case**. The case is assigned an immutable UUIDv4 and tracked in local SQLite storage.

### Stage 2: Evidence Ingestion & Cryptographic Sealing
1. Open the created case and switch to the **Evidence Vault** tab.
2. Drag and drop or browse to select raw claim photographs (supported: `.jpg`, `.jpeg`, `.png`, `.webp`, `.tiff`).
3. The platform immediately performs:
   - File signature magic-byte verification (rejecting MIME-spoofed binaries).
   - Decompression bomb threshold checks ($max\_pixels = 100,000,000$).
   - Cryptographic SHA-256 calculation.
   - Initial EXIF/TIFF metadata extraction (camera model, software tags, timestamp, GPS).
4. Review the generated Evidence Record. Verify that the SHA-256 matches the laboratory intake manifest.

### Stage 3: Running the Classical Forensics Suite
1. Select an ingested evidence image and click **Run Classical Forensics**.
2. The pipeline executes six parallel algorithmic filters:
   - **Error Level Analysis (ELA):** Detects differences in JPEG compression error rates across 95%, 90%, and 85% recompression baselines. Bright anomalies indicate candidate spliced or resaved regions.
   - **Noise Variance Inconsistency:** Measures local Laplacian and high-pass noise standard deviation across $32 \times 32$ tiles. Disparities highlight content composited from separate sensor sources.
   - **Copy-Move Candidate Detection:** Computes block-matching across SIFT / ORB keypoint descriptors to identify duplicated vehicle panels, clone-stamped scratches, or cloned foliage.
   - **CFA / Bayer Demosaicing Artifacts:** Analyzes chromatic channel phase correlations to verify whether camera sensor color filter array patterns are continuous across object boundaries.
   - **Metadata & EXIF Extraction:** Identifies software modification tags (e.g., `Photoshop 25.2`, `GIMP`, `Snapseed`), missing camera serials, or date/time inconsistencies.
   - **Perceptual Hashing (pHash, aHash, dHash):** Produces 64-bit structural fingerprints for duplicate and derivative indexing.
3. Review the forensic heatmaps, global anomaly score ($0.0 - 1.0$), and technique summaries.

### Stage 4: Interactive Forensic Canvas & Region of Interest (ROI) Analysis
1. Navigate to the **Forensic Canvas** (`/canvas`).
2. Load the primary evidence image alongside reference images (e.g., pre-loss inspection photograph or contrasting angle).
3. Utilize inspection tools:
   - **Dual Synchronized Pan/Zoom:** Zoom into micro-textures simultaneously across both viewports with locked coordinates (`Space + Drag`).
   - **Interactive Wipe & Curtain Splitter:** Slide the divider horizontally or vertically to compare structural alignment between baseline and claim photos.
   - **Difference Overlay / Heatmap Blend:** Toggle blending mode (`Difference`, `Exclusion`, `Threshold Delta`) to expose pixel deviations.
   - **ROI Selection & Tagging:** Use the polygon or rectangle tool to highlight suspicious regions (e.g., `ROI-01: Front bumper crease discontinuity`).
   - **Annotation Drawer:** Attach examiner observations, confidence ratings (Low, Medium, High), and investigative hypotheses.

### Stage 5: Quantum-Assisted Comparison Lab
1. Select an annotated $4 \times 4$ or $8 \times 8$ micro-patch from the primary evidence and a reference baseline patch.
2. Navigate to the **Quantum Lab** (`/quantum`).
3. Choose the Quantum Simulation Pipeline:
   - **Amplitude Encoding (16-Qubit / 12-Qubit Scheme):** Encodes normalized pixel amplitudes directly into pure quantum state vectors ($|\psi\rangle = \sum c_i |i\rangle$).
   - **Quantum State Tomography (QST):** Simulates measurement statistics to reconstruct density matrices ($\rho$).
   - **Quantum Distance Metrics:**
     - **Uhlmann Fidelity:** $F(\rho_1, \rho_2) = \left(\text{Tr}\sqrt{\sqrt{\rho_1}\rho_2\sqrt{\rho_1}}\right)^2$
     - **Trace Distance:** $D(\rho_1, \rho_2) = \frac{1}{2}\text{Tr}|\rho_1 - \rho_2|$
     - **Bhattacharyya Quantum Affinity:** Statistical overlap of projective measurement distributions.
4. Execute the simulation on the local Qiskit Aer Statevector simulator.
5. Inspect the fidelity curve, Bloch sphere state vectors, and measurement histograms. Verify whether sub-pixel interference signatures confirm or refute localized texture tampering.

### Stage 6: Dossier Studio & Report Generation
1. Navigate to the **Dossier Studio** (`/dossier`).
2. Select the active case to aggregate all case assets:
   - Ingested evidence records and SHA-256 digests.
   - Classical forensic heatmaps and anomaly ratings.
   - Annotated ROIs and canvas comparison notes.
   - Quantum fidelity curves and tomographic metrics.
3. Choose an export profile:
   - **Full Technical Dossier (PDF):** Multi-page, forensic laboratory-grade PDF containing executive summary, methodology notes, SHA-256 custody ledger, high-resolution visualizers, and conclusion disclaimer.
   - **Executive Summary (PDF):** 2-page brief summarizing overall findings and technical confidence.
   - **Machine-Readable Forensic JSON:** Cryptographically sealed JSON manifest for archiving and courtroom discovery indexing.
4. Click **Compile & Export**. Save the artifact locally to `storage/reports/`.

---

## 4. Keyboard Shortcuts Reference

| Shortcut | Action | Scope |
|:---|:---|:---|
| `Alt + N` | Create New Case | Global |
| `Alt + E` | Ingest Evidence File | Global |
| `Ctrl + F` | Search Cases / Evidence | Global |
| `Space + Drag` | Pan Viewport | Canvas 2D |
| `Scroll Wheel` | Zoom in / Zoom out | Canvas 2D |
| `[ / ]` | Toggle Inspection Channels | Canvas 2D |
| `Esc` | Cancel Current ROI Drawing | Canvas 2D |
| `Ctrl + S` | Save Active Annotations | Canvas 2D |
| `Ctrl + P` | Quick Export Dossier Preview | Dossier Studio |

---

## 5. Troubleshooting & Diagnostics

- **Backend Connection Failed:** Ensure the FastAPI server is running on `http://localhost:8000`. Run `python -m backend.main` from repository root.
- **Image Upload Rejected:** Confirm the file is a valid image (`JPEG`, `PNG`, `TIFF`, `WEBP`) and below the $50\text{ MB}$ limit. Verify the file is not corrupted or truncated.
- **Quantum Simulation Latency:** Quantum simulations with $\ge 16$ qubits execute on the local CPU Aer simulator. Ensure no other heavy computational processes are consuming RAM.
