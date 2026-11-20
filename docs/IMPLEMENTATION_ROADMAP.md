# Q-TRACE — Master Implementation Roadmap (Parts 2–10)

**Document ID:** `DOC-KB-011`  
**Classification:** Engineering Execution Roadmap & Phase Gate Specifications  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Scope:** Chronological Execution Specifications for Parts 2 through 10  

---

## 1. Roadmap Overview & Execution Philosophy

The development of Q-TRACE is structured across **ten disciplined, sequential parts**. To guarantee technical credibility, Part 2 immediately attacks the highest-risk technical hurdle (**the quantum comparison proof-of-concept**) before any full-scale frontend or database scaffolding is undertaken.

```
+---------------------------------------------------------------------------------------------------+
|                                Q-TRACE 10-PART ROADMAP TIMELINE                                   |
+---------------------------------------------------------------------------------------------------+
|  [PART 1: Master Research, Feasibility & Architecture]  <-- CURRENT MILESTONE (COMPLETED)         |
|                           |                                                                       |
|  [PART 2: Quantum Proof of Concept (Standalone Engine)] <-- NEXT IMMEDIATE TARGET                |
|                           |                                                                       |
|  [PART 3: Project Foundation, Storage & Core API]                                                 |
|                           |                                                                       |
|  [PART 4: Design System & Evidence Canvas UI]                                                     |
|                           |                                                                       |
|  [PART 5: Case Management & Cryptographic Evidence Ingestion]                                     |
|                           |                                                                       |
|  [PART 6: Classical Forensic Engine Implementation]                                               |
|                           |                                                                       |
|  [PART 7: Quantum Laboratory Full Integration]                                                    |
|                           |                                                                       |
|  [PART 8: Intelligence Fusion, RoI Engine & Canvas Overlays]                                      |
|                           |                                                                       |
|  [PART 9: Auditable Forensic Reporting & Security Hardening]                                       |
|                           |                                                                       |
|  [PART 10: Testing, Benchmarking, Documentation & Viva Preparation]                               |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Detailed Phase Specifications

---

### PART 2 — Quantum Proof of Concept (Standalone Engine)

- **Primary Objective:** Build a standalone, mathematically validated, test-covered Python/Qiskit prototype proving that $4 \times 4$ images can be encoded via NEQR, compared via coherent CNOT XOR, and reconstructed via Aer simulation.
- **Dependencies:** Part 1 completion; Python 3.11, Qiskit 1.0+, Qiskit Aer.
- **Major Tasks:**
  1. Implement `NEQRGrayscaleImage` circuit builder: 4 spatial qubits, 4 intensity qubits.
  2. Implement `QuantumImageComparator` supporting:
     - 16-qubit architecture (4 pos, 4 A, 4 B, 4 D).
     - 12-qubit in-place architecture (4 pos, 4 A, 4 B/Diff).
  3. Implement multi-controlled state preparation conditioned on pixel intensities.
  4. Implement bitwise CNOT comparison logic.
  5. Implement `DifferenceMapReconstructor` parsing QasmSimulator counts into a $4 \times 4$ numpy array.
  6. Implement an independent classical NumPy bitwise XOR verifier.
- **Deliverables:**
  - `src/quantum/circuit.py`
  - `src/quantum/comparator.py`
  - `src/quantum/reconstructor.py`
  - `tests/test_quantum_poc.py` (Automated pytest suite validating exact match against NumPy).
- **Acceptance Criteria:**
  - 100% test pass on identical patches ($D \equiv 0$).
  - 100% test pass on single-pixel and multi-pixel synthetic differences.
  - Verification that shot budget $S = 1024$ achieves complete difference map reconstruction.
- **Completion Condition:** Zero pending mathematical or circuit bugs; unit test suite executes cleanly under pytest on Windows.

---

### PART 3 — Project Foundation, Storage & Core API

- **Primary Objective:** Establish the production repository structure, SQLite database with Write-Ahead Logging (WAL), WORM evidence vault, and FastAPI service skeleton.
- **Dependencies:** Part 2 completion.
- **Major Tasks:**
  1. Initialize standard project hierarchy (`backend/`, `frontend/`, `storage/`, `docs/`, `tests/`).
  2. Implement SQLite schema (`schema.sql`): `cases`, `evidence_manifests`, `timeline_events`, `rois`.
  3. Implement `EvidenceVault` with SHA-256 calculation and read-only file enforcement.
  4. Scaffold FastAPI application (`backend/main.py`) with CORS, lifespan handlers, and router modules.
  5. Configure PowerShell development scripts (`scripts/dev.ps1`, `scripts/test.ps1`).
- **Deliverables:**
  - `backend/app/core/config.py`
  - `backend/app/db/database.py`
  - `backend/app/services/vault.py`
  - Working FastAPI server launching on `http://127.0.0.1:8000`.
- **Acceptance Criteria:**
  - Uploading a binary file creates an immutable entry in `storage/vault/` and returns its SHA-256 hash.
  - Attempting to overwrite an existing evidence record raises a database constraint error.

---

### PART 4 — UI/UX Design System & Evidence Canvas

- **Primary Objective:** Scaffold the modern React/Vite/TypeScript client and construct the high-performance HTML5 Canvas2D Evidence Canvas.
- **Dependencies:** Part 3 completion; Node.js v22+, npm 10+.
- **Major Tasks:**
  1. Initialize Vite React TypeScript project in `frontend/`.
  2. Install and configure Tailwind CSS with custom "Dark Laboratory" color palette (`#080C14`, `#0F172A`, `#00E5FF`, `#818CF8`).
  3. Build `EvidenceCanvas` component:
     - Off-screen buffer rendering.
     - Smooth zoom (10%–3200%) centered on cursor.
     - Spacebar-drag panning with inertia damping.
     - Coordinate HUD readout `(X, Y)`.
  4. Implement interactive `SplitWipeComparison` divider slider.
  5. Build layer visibility toggle bar and opacity sliders.
- **Deliverables:**
  - `frontend/src/components/canvas/EvidenceCanvas.tsx`
  - `frontend/src/components/canvas/SplitWipeSlider.tsx`
  - `frontend/src/styles/theme.css`
- **Acceptance Criteria:**
  - Smooth 60 FPS panning and zooming of a 12-megapixel photograph on standard laptop display.
  - Pixel grid overlay appears cleanly at $\ge 400\%$ zoom.

---

### PART 5 — Case Management & Cryptographic Ingestion

- **Primary Objective:** Implement the complete end-to-end evidence ingestion workflow with full validation and metadata extraction.
- **Dependencies:** Parts 3 and 4.
- **Major Tasks:**
  1. Build Case Creation and Case List views in React.
  2. Implement file upload dropzone with client-side format filtering.
  3. Implement backend decompression bomb guard (`Image.MAX_IMAGE_PIXELS`).
  4. Implement EXIF and C2PA metadata extractor using Pillow and PyExifTool.
  5. Generate normalized sRGB working derivatives.
  6. Record ingestion event in the cryptographic timeline.
- **Deliverables:**
  - `backend/app/api/cases.py`
  - `backend/app/api/evidence.py`
  - `frontend/src/views/CaseDetailView.tsx`
- **Acceptance Criteria:**
  - An investigator can create a case, upload two vehicle photos, inspect their SHA-256 digests, and view extracted camera metadata.

---

### PART 6 — Classical Forensic Engine Implementation

- **Primary Objective:** Implement and optimize the five core classical forensic algorithms as asynchronous worker services.
- **Dependencies:** Part 5 completion; OpenCV, Pillow, SciPy.
- **Major Tasks:**
  1. Build `ELAAnalyzer`: in-memory JPEG resave at $Q=95$, error delta amplification.
  2. Build `SIFTCopyMoveDetector`: keypoint extraction, Lowe's ratio matching, spatial distance thresholding, affine clustering.
  3. Build `NoiseVarianceFilter`: adaptive median residual calculation, overlapping block variance.
  4. Build `GradientDeltaAnalyzer`: Sobel gradient magnitude, Laplacian texture drop.
  5. Build `ReferenceSSIMComparator`: homography alignment, SSIM discrepancy mapping.
  6. Implement background analysis dispatcher with task progress reporting.
- **Deliverables:**
  - `backend/app/forensics/ela.py`
  - `backend/app/forensics/copymove.py`
  - `backend/app/forensics/noise.py`
  - `backend/app/forensics/gradient.py`
  - `backend/app/forensics/comparator.py`
- **Acceptance Criteria:**
  - All five algorithms execute across a 12 MP test photo in $< 1.5 \text{ seconds}$ combined.
  - Unit tests verify detection of synthetic copy-move and splicing cases from CoMoFoD.

---

### PART 7 — Quantum Laboratory Full Integration

- **Primary Objective:** Integrate the Part 2 Quantum Engine into the FastAPI backend and connect it to the React Quantum Laboratory UI.
- **Dependencies:** Parts 2, 4, and 6.
- **Major Tasks:**
  1. Implement `POST /api/cases/{case_id}/quantum/simulate` endpoint:
     - Ingests coordinate `(x, y)` and shot count $S$.
     - Extracts $4 \times 4$ tile from evidence and reference derivatives.
     - Compiles and runs 16-qubit Qiskit Aer circuit.
     - Generates SVG circuit diagram using Qiskit circuit drawer.
  2. Build `QuantumLabModal` in React:
     - Qubit register inspector with color-coded badges.
     - Interactive SVG circuit viewer.
     - Shot budget slider ($16 \dots 4096$).
     - Probability distribution histogram (Plotly / Recharts).
     - Reconstructed difference tile vs. classical difference tile.
- **Deliverables:**
  - `backend/app/api/quantum.py`
  - `frontend/src/components/quantum/QuantumLabModal.tsx`
  - `frontend/src/components/quantum/ShotHistogram.tsx`
- **Acceptance Criteria:**
  - Clicking "Send to Quantum Lab" on the Evidence Canvas loads the patch, executes the circuit in $< 250 \text{ ms}$, renders the SVG circuit, and displays the reconstructed difference map.

---

### PART 8 — Intelligence Fusion, RoI Engine & Canvas Overlays

- **Primary Objective:** Connect classical heatmaps to the interactive Canvas, implement weighted consensus scoring, and build the Region Inspector drawer.
- **Dependencies:** Parts 6 and 7.
- **Major Tasks:**
  1. Implement `FusionCoordinator`: normalize heatmaps, calculate weighted sum, apply morphological opening/dilation.
  2. Extract contiguous RoI contours and generate coordinate bounding boxes.
  3. Implement Canvas2D heatmap overlay rendering with adjustable opacity.
  4. Build `RegionInspector` drawer:
     - 1:1 image crop of selected RoI.
     - Contributing algorithmic score bars.
     - Contextual forensic explanation.
     - Examiner notes text input.
- **Deliverables:**
  - `backend/app/forensics/fusion.py`
  - `frontend/src/components/canvas/RegionOverlay.tsx`
  - `frontend/src/components/inspector/RegionInspector.tsx`
- **Acceptance Criteria:**
  - Suspicious regions automatically appear as clickable bounding boxes on the Canvas; clicking a box opens its evidence breakdown and allows note entry.

---

### PART 9 — Auditable Forensic Reporting & Security Hardening

- **Primary Objective:** Build the court-ready PDF dossier generator and perform a comprehensive security audit of file handling and input paths.
- **Dependencies:** Parts 5, 6, 7, and 8; ReportLab.
- **Major Tasks:**
  1. Build `PDFReportGenerator`:
     - Clean typographic layout matching the "Dark Laboratory" branding.
     - Case details, evidence SHA-256 hashes, and timestamp manifests.
     - Side-by-side original and suspect image figures.
     - Individual heatmap plates (ELA, SIFT, Noise, Fusion).
     - Quantum Laboratory experiment plates (circuit diagram, measurement histogram, difference tile).
     - Examiner notes and methodological limitation disclaimers.
  2. Security hardening: verify path traversal guards, sanitize filenames, audit SQLite queries.
- **Deliverables:**
  - `backend/app/services/reporting.py`
  - `backend/app/core/security.py`
  - Test suite generating verified PDF reports.
- **Acceptance Criteria:**
  - Generates a polished, multi-page, court-admissible PDF report in $< 2 \text{ seconds}$ with embedded SHA-256 verification blocks.

---

### PART 10 — Testing, Benchmarking, Documentation & Viva Delivery

- **Primary Objective:** Execute the 12 experiments from `EXPERIMENT_PLAN.md`, compile performance benchmarks, prepare demonstration datasets, and produce complete university viva materials.
- **Dependencies:** Parts 1 through 9.
- **Major Tasks:**
  1. Execute automated benchmark scripts across CASIA, CoMoFoD, and Q-TRACE-AutoDamage-Bench.
  2. Generate classical vs. quantum runtime and memory comparison tables.
  3. Assemble 5 realistic demonstration cases (including vehicle damage fraud).
  4. Write comprehensive User Manual and Developer Guide (`README.md`).
  5. Produce University Viva Defense Pack:
     - 15-slide PowerPoint / PDF presentation deck.
     - Whiteboard derivation cheat-sheet for quantum state preparation and XOR logic.
     - Scripted examiner Q&A preparation guide addressing all potential critiques.
- **Deliverables:**
  - `tests/benchmark_suite.py`
  - `demo_cases/` (sample packaged claim investigations)
  - `docs/VIVA_PREPARATION_GUIDE.md`
  - `README.md` (clean, verified installation and run instructions)
- **Acceptance Criteria:**
  - All automated tests pass; application launches from clean environment via single PowerShell script; the student can flawlessly demonstrate the platform and answer all viva questions.

---

*Continue to `TECHNICAL_DECISIONS.md` for the formal Architectural Decision Records (ADRs).*

