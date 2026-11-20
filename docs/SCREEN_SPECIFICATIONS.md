# Q-TRACE Workstation Screen Specifications

## 1. Screen Catalog & States Matrix

| Screen ID | Title | Route | Primary API Endpoint | States Handled |
| :--- | :--- | :--- | :--- | :--- |
| **SCR-01** | Command Center | `/` | `GET /api/v1/cases`, `GET /api/v1/evidence`, `GET /api/v1/system/info` | Loading, Empty, Populated, Error |
| **SCR-02** | Investigations Register | `/investigations` | `GET /api/v1/cases?page={p}&page_size={s}` | Loading, Empty, Populated, Search/Filter |
| **SCR-03** | Create Investigation | `/investigations/new` | `POST /api/v1/cases` | Pristine, Validating, Submitting, Conflict Error |
| **SCR-04** | Investigation Dossier Detail | `/investigations/:caseId` | `GET /api/v1/cases/{id}`, `GET /cases/{id}/evidence`, `POST /cases/{id}/notes` | Loading, Populated, Tab Switch, Upload Modal |
| **SCR-05** | Preserved Evidence Library | `/evidence` | `GET /api/v1/evidence?page={p}&page_size={s}` | Loading, Empty, Populated, Filter |
| **SCR-06** | Evidence Ingestion | `/evidence/upload` | `GET /api/v1/cases`, `POST /cases/{id}/evidence` | File Drop, Preview, Uploading, Ingested |
| **SCR-07** | Evidence Detail & Audit | `/evidence/:evidenceId` | `GET /api/v1/evidence/{id}`, `POST /evidence/{id}/verify` | Canvas Viewer, Auditing, Verified, Compromised |
| **SCR-08** | Analysis Workspace | `/analysis` | `GET /api/v1/evidence` | Evidence Selector, Module Catalog |
| **SCR-09** | Quantum Laboratory | `/quantum-lab` | `POST /api/v1/quantum/compare` | Presets, 4×4 Grid Edit, Simulating, Telemetry Results |
| **SCR-10** | Findings Taxonomy | `/findings` | Pure evidentiary presentation | Static 4-Category Legal Taxonomy |
| **SCR-11** | Reporting Dossier | `/reports` | `GET /api/v1/cases`, `GET /cases/{id}` | Dossier Compilation, Notes Ledger, PDF Boundary |
| **SCR-12** | System Diagnostics | `/settings` | `GET /api/v1/system/info` | Loading, Telemetry Display, Error |

---

## 2. Detailed Screen Specifications

### SCR-01 — Command Center (`/`)
- **Visual Structure**: 4 quick stat cards (Total Cases, Preserved Evidence, WORM Status, Quantum Simulator), 2-column main area (Active Cases list, Recent Evidence list, Quick Action cards, and live System Readiness card).
- **Empty State**: Renders `EmptyState` component with guided prompt to register first case.
- **Error Handling**: Displays top alert banner with retry button.

### SCR-02 — Investigations Register (`/investigations`)
- **Visual Structure**: Search input (queries case number, title, description), status pills (`ALL`, `OPEN`, `IN_PROGRESS`, `CLOSED`, `ARCHIVED`), interactive table with case numbers, titles, status badges, creation timestamps, and "Review File" buttons.
- **Pagination**: Supports forward/backward navigation with total count display.

### SCR-03 — Create Investigation (`/investigations/new`)
- **Inputs**: Case number (with "Generate Identifier" helper), Investigation Title, Description textarea.
- **Client Validation**: Enforces minimum 3 characters on case number and title.
- **Error Behavior**: Catches 409 Conflict from backend and advises user to select a unique case number.
- **Success Action**: Seamlessly navigates to `/investigations/{created.id}`.

### SCR-04 — Investigation Dossier Detail (`/investigations/:caseId`)
- **Case Header**: Shows case number, status badge, title, narrative, creation timestamp, and inline status switcher (`OPEN`, `IN_PROGRESS`, `CLOSED`, `ARCHIVED`).
- **Tab 1: Evidence Vault**:
  - Grid of evidence cards showing thumbnail preview, original filename, dimensions, size, SHA-256 hash snippet, and "Inspect Evidence" button.
  - "Ingest Image Evidence" button opens accessible upload modal with file picker, drag-and-drop, and pre-flight validation.
- **Tab 2: Examiner Observations**:
  - Form to record new observations with Author and Content fields.
  - Chronological list of recorded notes with author and timestamp.
- **Tab 3: Forensic Analysis Runs**:
  - Overview of automated pipelines and direct link to Quantum Lab.

### SCR-05 — Preserved Evidence Library (`/evidence`)
- **Visual Structure**: Search bar (filename, hash), status filters (`ALL`, `VERIFIED`, `COMPROMISED`), responsive card grid displaying visual thumbnail, MIME type, dimensions, file size, SHA-256 hash, and "Inspect File" link.

### SCR-06 — Evidence Ingestion (`/evidence/upload`)
- **Form Controls**: Case dropdown selector, dashed file drop zone accepting JPEG, PNG, TIFF, pre-flight file size and preview card, submission button with loading spinner.
- **Success Action**: Redirects directly to `/evidence/{id}`.

### SCR-07 — Evidence Detail & Audit (`/evidence/:evidenceId`)
- **Forensic Image Viewer**:
  - Canvas viewport with zoom (0.5× to 5.0×), smooth pan/drag, 1:1 pixel mode, reset fit, and real-time cursor coordinate crosshair (`X: px, Y: px`).
  - WORM status banner and SHA-256 display.
- **On-Demand Audit Card**:
  - "Audit Bitstream Integrity" button calling `POST /api/v1/evidence/{id}/verify`.
  - Displays instant verification badge (`VERIFIED` or `COMPROMISED`), timestamp, and hash comparison.
- **Chain of Custody Ledger**:
  - Complete technical attributes: UUID, original filename, stored filename, storage path, MIME, byte length, dimensions, full SHA-256 digest, ingestion timestamp.

### SCR-08 — Analysis Workspace (`/analysis`)
- **Controls**: Evidence selector dropdown.
- **Module Catalog**: Cards for Quantum NEQR Patch Comparison (Active), Classical XOR Difference (Active), Error Level Analysis (Planned Part 5), and Wavelet Noise Inconsistency (Planned Part 5).

### SCR-09 — Quantum Laboratory (`/quantum-lab`)
- **Signature UI Component**:
  - Dual 4×4 pixel grid inputs for Patch A and Patch B with color-scaled intensity backgrounds (values 0 to 15).
  - Presets: Single-Pixel Tamper, Object Splicing, Identical Patches, Corner Boundary.
  - Architecture selector: 16-Qubit NEQR vs 12-Qubit In-Place.
  - Shot count selector: 100, 200, 500, 1024, 2048 shots.
  - "Execute Quantum Simulation" button calling real backend API.
- **Results Display**:
  - Telemetry badges: Qubits, Circuit Depth, Total Gates, Sampling Coverage, Shots Measured, Runtime (ms).
  - Visual 4×4 Quantum Reconstructed Difference Map heatmap highlighting tampered coordinates.
  - Classical Ground Truth 4×4 Difference Map.
  - Scientific transparency callout note.

### SCR-10 — Findings Taxonomy (`/findings`)
- **Educational & Legal Structure**: 4 distinct categories:
  1. Directly Observed Technical Facts (hashes, WORM permissions).
  2. Algorithmic Simulation Outputs (quantum fidelity, coupon bounds).
  3. Potential Manipulation Indicators (pixel disparities, compression edges).
  4. Examiner Hypotheses (qualitative notes, collision context).

### SCR-11 — Reporting Dossier (`/reports`)
- **Dossier Preview**: Case selector, incident narrative summary, cryptographic evidence inventory, examiner chronology, scientific methodology, and export boundary.

### SCR-12 — System Diagnostics (`/settings`)
- **Real-Time Telemetry**: Live status cards for Database (Dialect, WAL mode, Foreign keys), Physical Storage (WORM status, root path, directory verification), and Quantum Core (Qiskit version, AerSimulator availability, target backend).

