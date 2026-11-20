# Q-TRACE — System Architecture & Technology Specification

**Document ID:** `DOC-KB-008`  
**Classification:** Technical Architecture & System Engineering Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Runtime Target:** Local Windows 11 Development & Demonstration Environment  

---

## 1. Architectural Principles & System Context

Q-TRACE is engineered as a **Local-First, High-Performance Scientific Workstation**. It deliberately rejects unnecessary cloud microservices, external database servers, and SaaS dependencies in favor of an **ultra-reliable, self-contained desktop-web architecture**.

### Core Engineering Principles:
1. **Local & Confidential:** Forensic imagery and insurance claims must remain private; zero data leaves the investigator's local workstation.
2. **Deterministic & Auditable:** Given an identical input image and algorithm parameters, the system must output identical checksums, heatmaps, and difference matrices every time.
3. **Decoupled Frontend & Backend:** A high-speed FastAPI asynchronous service powers the scientific calculations, while a modern React/Vite/TypeScript client delivers sub-millisecond 60 FPS Canvas2D image interactions.
4. **Resilient to Hardware Constraints:** Fully executable on standard Windows laptops (Python 3.11, Intel/AMD multi-core CPU, 8–16 GB RAM) without requiring an external GPU or access to cloud-based quantum mainframes.

---

## 2. High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                  Q-TRACE SYSTEM ARCHITECTURE                                      |
+---------------------------------------------------------------------------------------------------+
                                                  |
                               [ HTTP / REST / WebSocket ]
                                                  |
+-------------------------------------------------v-------------------------------------------------+
|                       PRESENTATION TIER (React 18 + Vite + TypeScript)                            |
|  +--------------------+  +----------------------+  +---------------------+  +------------------+  |
|  |   Case Dashboard   |  |   Evidence Canvas    |  |   Region Inspector  |  |   Quantum Lab    |  |
|  |  (Case metadata &  |  |  (Pan/Zoom, Layers,  |  |  (RoI Metrics, Notes|  |  (SVG Circuit,   |  |
|  |   Timeline audit)  |  |   Split-wipe Slider) |  |   & Q-Lab Handoff)  |  |   Shot Histogram) |  |
|  +--------------------+  +----------------------+  +---------------------+  +------------------+  |
+-------------------------------------------------^-------------------------------------------------+
                                                  |
                                        [ FastAPI REST API ]
                                                  |
+-------------------------------------------------v-------------------------------------------------+
|                         APPLICATION SERVICE TIER (Python 3.11 + FastAPI)                          |
|                                                                                                   |
|  +--------------------------+  +--------------------------+  +---------------------------------+  |
|  |  Evidence Ingestion Hub  |  |  Classical Forensics Svc |  |    Quantum Simulation Engine    |  |
|  |  - SHA-256 Hashing       |  |  - ELA Analyzer          |  |  - NEQR State Superposition     |  |
|  |  - MIME & Bomb Guard     |  |  - SIFT Copy-Move Matcher|  |  - Multi-Controlled Gate Prep  |  |
|  |  - WORM Vault Storage    |  |  - Noise Variance Filter |  |  - Coherent CNOT XOR Unitary    |  |
|  |  - EXIF / C2PA Parser    |  |  - Boundary Gradient     |  |  - Qiskit Aer Shot Simulator    |  |
|  |                          |  |  - Reference SSIM Delta  |  |  - Coupon Collector Sampler     |  |
|  +--------------------------+  +--------------------------+  +---------------------------------+  |
|                                              |                                                    |
|  +-------------------------------------------v-------------------------------------------------+  |
|  |                           Intelligence & Evidence Fusion Coordinator                         |  |
|  |                   - Weighted Multi-Signal Heatmap Normalization                             |  |
|  |                   - Morphological Contour Clustering & RoI Extraction                       |  |
|  +-------------------------------------------^-------------------------------------------------+  |
+----------------------------------------------|----------------------------------------------------+
                                               |
+----------------------------------------------v----------------------------------------------------+
|                         STORAGE & DATA PERSISTENCE TIER (Local Disk)                              |
|                                                                                                   |
|  +-------------------------------+   +---------------------------------------------------------+  |
|  |     SQLite Database (WAL)     |   |                   Local File Vault                      |  |
|  |  - cases                      |   |  storage/                                               |  |
|  |  - evidence_manifests         |   |    ├── vault/       # Immutable WORM original files     |  |
|  |  - roi_annotations            |   |    ├── derivatives/ # Normalized working copies         |  |
|  |  - timeline_events            |   |    ├── patches/     # 4x4 & 8x8 tiles for Q-Lab         |  |
|  |  - quantum_experiments        |   |    └── reports/     # Cryptographically signed PDFs     |  |
|  +-------------------------------+   +---------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Technology Stack Selection & Rationales

| Subsystem | Selected Technology | Alternatives Evaluated | Technical Justification |
| :--- | :--- | :--- | :--- |
| **Backend API** | **FastAPI (Python 3.11)** | Flask, Django, Node.js Express | High-performance asynchronous event loop; native integration with Python scientific libraries (NumPy, OpenCV, Qiskit); automated OpenAPI documentation; strict Pydantic type validation. |
| **Frontend Framework** | **React 18 + Vite + TypeScript** | Streamlit, Next.js, Vue 3 | Streamlit was evaluated and **rejected** because its reactive rerun model prevents smooth 60 FPS pan/zoom, interactive split-screen wipes, and custom canvas overlays. React + Vite provides instant HMR, full client-side state control, and modern modularity. |
| **Canvas Rendering** | **HTML5 Canvas2D / WebGL** | SVG, DOM Img elements | Direct per-pixel buffer rendering (`ImageData`), instantaneous colormap transformations, hardware-accelerated pan and zoom without DOM lag. |
| **Quantum Engine** | **IBM Qiskit 1.0+ & Qiskit Aer** | PennyLane, Cirq, ProjectQ | Qiskit is the undisputed academic benchmark for university courses; Qiskit Aer provides a highly optimized C++ state vector and QASM simulator executable locally on Windows. |
| **Computer Vision** | **OpenCV (headless), Pillow, SciPy** | PyTorch, scikit-image only | Fast C++ implementations of SIFT, DCT, median filters, and morphologic operations with minimal CPU footprint. |
| **Case Database** | **SQLite 3 (with WAL Mode)** | PostgreSQL, MongoDB | Zero installation overhead, serverless, single-file portability, ACID compliant. Write-Ahead Logging (WAL) enables concurrent reads during analysis writes. |
| **Dossier Reporting**| **ReportLab** | WeasyPrint, Puppeteer headless | Pure Python PDF generation with precise millimeter coordinate layout; zero Chromium/headless browser overhead; deterministic byte generation. |

---

## 4. Component Responsibilities & Data Flow

### 4.1 Ingestion & Evidence Vault (WORM Standard)
1. **Intake:** The investigator uploads an image via `POST /api/cases/{case_id}/evidence`.
2. **Sanitization:** File extension and magic byte headers are validated. Pillow verifies image dimensions against decompression bombs (`Image.MAX_IMAGE_PIXELS = 100_000_000`).
3. **Hashing:** Raw bytes are streamed through `hashlib.sha256()`.
4. **WORM Preservation:** File is stored in `storage/vault/{sha256}.bin` with read-only file attributes. An evidence record is created in SQLite.
5. **Derivative Generation:** A normalized working derivative (sRGB, orientation corrected) is saved in `storage/derivatives/{evidence_id}.png`.

### 4.2 Classical Analysis Pipeline
1. Ingestion triggers an asynchronous background pipeline executing five analysis workers:
   - Worker 1: `compute_ela(derivative_path, quality=95, scale=15)`
   - Worker 2: `compute_sift_cmfd(derivative_path, ratio=0.65, min_dist=30)`
   - Worker 3: `compute_noise_variance(derivative_path, block_size=16)`
   - Worker 4: `compute_gradient_delta(derivative_path)`
   - Worker 5: `extract_metadata_and_c2pa(original_path)`
2. Outputs are converted to compressed grayscale PNG heatmaps and registered with the Case Repository.
3. The Fusion Coordinator calculates the weighted consensus map and extracts bounding boxes for all candidate RoIs.

### 4.3 Quantum Laboratory Pipeline
1. When the user requests a quantum verification on patch coordinates `(x, y)`:
2. The backend extracts a $4 \times 4$ tile from the reference and test images, quantizing intensities to 4 bits ($0..15$).
3. The Quantum Service compiles the 16-qubit Qiskit circuit:
   - $H^{\otimes 4}$ on position qubits.
   - $C^4(NOT)$ state preparation encoding pixel arrays.
   - 8 CNOT gates for bitwise XOR.
4. Circuit is submitted to `qiskit_aer.AerSimulator` with the requested shot count (e.g., $S = 1024$).
5. Measurement dictionary is decoded: basis states are parsed, spatial difference matrix is reconstructed, and circuit SVG + execution statistics are returned to the client.

---

## 5. REST API Specification (OpenAPI Schema)

```
Endpoint                                    | Method | Description
--------------------------------------------+--------+------------------------------------------------------
/api/cases                                  | GET    | List all forensic investigation cases
/api/cases                                  | POST   | Create a new investigation case (case_id, title)
/api/cases/{case_id}                        | GET    | Retrieve case details, evidence list, and timeline
/api/cases/{case_id}/evidence               | POST   | Upload evidence photograph (multipart/form-data)
/api/cases/{case_id}/evidence/{evidence_id} | GET    | Get evidence manifest, SHA-256, and metadata
/api/cases/{case_id}/analyze                | POST   | Trigger classical forensic scan on evidence
/api/cases/{case_id}/heatmaps/{method}      | GET    | Retrieve analysis heatmap image stream (PNG)
/api/cases/{case_id}/rois                   | GET    | List detected suspicious RoI bounding boxes
/api/cases/{case_id}/rois/{roi_id}/notes    | POST   | Append examiner notes to a specific RoI
/api/cases/{case_id}/quantum/simulate       | POST   | Run 16-qubit Qiskit simulation on patch (x, y, shots)
/api/cases/{case_id}/report                 | POST   | Generate and sign court-ready PDF dossier
/api/cases/{case_id}/report/download        | GET    | Download compiled PDF report
```

---

## 6. Security, Storage & Defensive Engineering

### 6.1 Path Traversal Prevention
All file accesses strictly validate path boundaries using `os.path.abspath()` and `os.path.commonpath()` to ensure operations never escape the designated `storage/` directory:
```python
def resolve_secure_path(base_dir: Path, filename: str) -> Path:
    clean_name = os.path.basename(filename)
    target = (base_dir / clean_name).resolve()
    if not str(target).startswith(str(base_dir.resolve())):
        raise PermissionError("Path traversal attempt detected.")
    return target
```

### 6.2 Decompression Bomb & Resource Exhaustion Defense
A malicious actor could upload a 50 kilobyte PNG file that decompresses into 10 gigabytes of memory ("zip bomb"). Q-TRACE enforces:
```python
from PIL import Image
Image.MAX_IMAGE_PIXELS = 100_000_000  # Cap at 100 Megapixels
MAX_UPLOAD_BYTES = 50 * 1024 * 1024   # 50 MB file upload limit
```

### 6.3 Immutable SQLite WORM Audit Logging
The case database uses triggers to prevent modification or deletion of evidence manifests and historical timeline events:
```sql
CREATE TRIGGER prevent_evidence_mutation
BEFORE UPDATE ON evidence_manifests
BEGIN
    SELECT RAISE(FAIL, 'Evidence manifests are cryptographically immutable.');
END;
```

---

*Continue to `EXPERIMENT_PLAN.md` for the detailed 12-experiment research and benchmarking plan.*

