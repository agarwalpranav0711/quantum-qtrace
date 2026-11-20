# Q-TRACE: Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform

[![Version](https://img.shields.io/badge/Version-1.0.0--Production-blue.svg)](https://github.com/agarwalpranav0711/quantum-qtrace)
[![Architecture](https://img.shields.io/badge/Architecture-Local--First%20%7C%20Zero--Cloud-brightgreen.svg)](docs/ARCHITECTURE.md)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-orange.svg)](backend/)
[![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%7C%20TypeScript%20%7C%20Vite-cyan.svg)](frontend/)
[![Quantum](https://img.shields.io/badge/Quantum%20Simulation-Qiskit%201.0+-blueviolet.svg)](docs/RESEARCH_METHODOLOGY.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 1. Executive Overview & Product Identity

**Q-TRACE** is a local-first, software-only digital image forensics and evidence intelligence workstation. 

Initially engineered for motor-vehicle insurance fraud investigations, Q-TRACE equips forensic examiners, Special Investigation Units (SIU), and digital forensics researchers with an integrated suite of classical statistical signal filters, an interactive multi-viewport forensic canvas, and experimental quantum state simulation for high-precision micro-texture comparison.

### Key Architectural Mandates
- **100% Local-First & Zero-Cloud:** Operates entirely within the user's local operating environment on `localhost`. Requires zero cloud subscriptions, external API keys, container runtimes, or network connectivity. Fully air-gapped capable.
- **Strict Evidence Integrity:** Cryptographically seals ingested images via SHA-256 digests under a Write-Once, Read-Many (WORM) storage model.
- **Scientific Decision Support:** Strictly decision-support software. Q-TRACE does **NOT** make automated legal determinations or declare an image fraudulent. Findings are presented as transparent technical measurements requiring human expert adjudication.

---

## 2. System Architecture & Component Diagram

```
                                  +-----------------------------------------------+
                                  |            INVESTIGATOR WORKSTATION           |
                                  |     Google Chrome / Edge (Chromium Engine)    |
                                  +-----------------------------------------------+
                                                         |
                                                  HTTP / REST API
                                              (localhost:8000/api/v1)
                                                         |
                                                         v
+--------------------------------------------------------------------------------------------------------------------+
|                                              Q-TRACE CORE BACKEND (FASTAPI)                                        |
|                                                                                                                    |
|   +-----------------------+   +------------------------+   +-----------------------+   +-----------------------+   |
|   |   Evidence Vault      |   |   Classical Forensics  |   |   Interactive Canvas  |   |   Quantum Micro-Patch |   |
|   |   - SHA-256 Sealer    |   |   - Error Level (ELA)  |   |   - Dual Synchronized |   |     Simulator (Qiskit)|   |
|   |   - Magic-Byte Audit  |   |   - Noise Variance     |   |     Pan & Zoom        |   |   - Amplitude Encoding|   |
|   |   - EXIF/TIFF Parser  |   |   - Copy-Move (SIFT)   |   |   - Curtain Wipe      |   |   - State Tomography  |   |
|   |   - Decompress Guard  |   |   - CFA Demosaicing    |   |   - Dynamic Blend     |   |   - Uhlmann Fidelity  |   |
|   |   - WORM Disk Storage |   |   - Perceptual Hashes  |   |   - ROI Annotation    |   |   - Trace Distance    |   |
|   +-----------------------+   +------------------------+   +-----------------------+   +-----------------------+   |
|               |                            |                           |                           |               |
|               +----------------------------+---------------------------+---------------------------+               |
|                                                         |                                                          |
|                                                         v                                                          |
|                                       +-----------------------------------+                                        |
|                                       |   Dossier & Report Generator      |                                        |
|                                       |   - ReportLab Multi-Page PDF      |                                        |
|                                       |   - Courtroom Evidence Ledger     |                                        |
|                                       |   - Machine-Readable JSON         |                                        |
|                                       +-----------------------------------+                                        |
+--------------------------------------------------------------------------------------------------------------------+
                                       |                                   |
                                       v                                   v
                        +----------------------------+      +----------------------------+
                        |  SQLite Relational Store   |      |  WORM Local File Storage   |
                        |  (qtrace.db)               |      |  (storage/originals/,      |
                        |  - Cases, Evidence Registry|      |   derivatives/, reports/)  |
                        +----------------------------+      +----------------------------+
```

---

## 3. Real-World Motor-Vehicle Insurance Use Case

In automobile casualty and property claims, fraudulent submissions frequently involve:
1. **Clone-Stamping Scratches / Dents:** Duplicating minor bumper scuffs across multiple panels to inflate repair estimates.
2. **Foreign Part Splicing:** Digitally inserting severe collision damage, cracked headlights, or deployed airbags from separate vehicle accidents.
3. **Pre-Existing Damage Erasure:** Inpainting over prior rust, pre-existing fender dents, or registration marks prior to inception of insurance coverage.
4. **Contrast / Severity Enhancement:** Digitally sharpening superficial scuffs to mimic deep structural frame intrusion.

Q-TRACE isolates these physical and digital anomalies by cross-referencing compression history, sensor pattern noise, demosaicing continuity, and micro-texture geometry.

---

## 4. Forensic Decision-Support Disclaimer

> [!IMPORTANT]
> **LEGAL & FORENSIC ADMISSIBILITY NOTICE**  
> Q-TRACE is an evidentiary decision-support tool designed to assist qualified forensic examiners. It does **NOT** declare an image fraudulent, invalid, or forged. Technical anomalies (such as compression discrepancies or low quantum fidelity scores) can occur naturally due to multi-platform transmission (e.g., WhatsApp, MMS), OEM smartphone computational photography pipelines (Night Mode, HDR fusion), or non-uniform reflective surfaces (wax, rain, glare). Every finding must be evaluated, corroborated, and signed off by a human investigator.

---

## 5. Comprehensive Feature Matrix (Milestones 1–10)

| Module / Milestone | Capabilities & Forensic Tools |
|:---|:---|
| **Case & Evidence Vault (Parts 1-3)** | Multi-case management, cryptographic SHA-256 ingestion sealing, magic-byte inspection, WORM storage isolation, automated EXIF/TIFF extraction, live SHA-256 re-verification. |
| **Classical Forensics (Part 5)** | Multi-scale Error Level Analysis (95/90/85 Q), tile-based noise variance inconsistency ($32 \times 32$), SIFT/ORB copy-move keypoint clustering, CFA Bayer demosaicing periodicity, perceptual hashing (pHash, aHash, dHash). |
| **Forensic Canvas & ROI (Part 6)** | High-precision Canvas2D viewport, dual synchronized pan/zoom (up to 3200%), interactive curtain wipe, difference & exclusion blending, polygon/rect ROI markup, examiner notes drawer. |
| **Dossier & Reporting (Part 7)** | Multi-page laboratory-grade PDF compiler via ReportLab, high-resolution forensic heatmap embedding, chain-of-custody ledger, machine-readable JSON exports. |
| **Integration & Hardening (Part 8)** | Decompression bomb mitigation ($100\text{ MP}$ limit), canonical path traversal defense, file type whitelisting, Vitest UI testing, end-to-end integration validation. |
| **Research & Evaluation (Part 9)** | 120-image synthetic tampering benchmark, Coupon Collector shot bounds, ablation study across classical modules, quantum vs. classical sensitivity evaluation. |
| **Completion & Packaging (Part 10)** | Production hardening, comprehensive documentation suite, capstone whitepaper, repository hygiene, and clean local execution runbooks. |

---

## 6. Complete Technology Stack

- **Core Backend Framework:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Image Processing & Computer Vision:** OpenCV (headless), Pillow (PIL), NumPy, SciPy
- **Quantum State Simulation:** Qiskit 1.0+, Qiskit Aer (CPU Statevector Simulator)
- **Database & Storage:** SQLite3, SQLAlchemy ORM, Local WORM Filesystem
- **Reporting & Visualization:** ReportLab, Matplotlib
- **Frontend Architecture:** React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Canvas2D API
- **Testing & Verification:** Pytest, AnyIO, Vitest, Testing Library

---

## 7. Local Installation & Setup Runbook (Windows)

### Prerequisites
- **Windows 10 / 11 (64-bit)**
- **Python 3.11+** installed and added to `PATH`
- **Node.js v20+** and **npm** installed

### Step 1: Clone Repository
```powershell
git clone https://github.com/agarwalpranav0711/quantum-qtrace.git
cd "quantum-qtrace"
```

### Step 2: Backend Environment Configuration
```powershell
# Create Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Initialize environment configuration
Copy-Item .env.example .env
```

### Step 3: Frontend Environment Configuration
```powershell
cd frontend
npm install
cd ..
```

---

## 8. Launching Q-TRACE Locally

### Option A: Simultaneous One-Click Launch (Dual Terminals)
**Terminal 1 (Backend Server):**
```powershell
.\venv\Scripts\Activate.ps1
python -m backend.main
# Server runs on http://localhost:8000 (Swagger docs at /docs)
```

**Terminal 2 (Frontend Client):**
```powershell
cd frontend
npm run dev
# Vite client runs on http://localhost:5173
```

### Option B: Automated Windows PowerShell Runner
```powershell
.\scripts\run_local.ps1
```

---

## 9. Default Ports & Service Endpoints

| Service / Interface | Local Endpoint | Description |
|:---|:---|:---|
| **Frontend Web Client** | `http://localhost:5173` | Investigator Workstation GUI |
| **Backend REST API** | `http://localhost:8000/api/v1` | Core Forensics API Base |
| **Interactive API Docs** | `http://localhost:8000/docs` | OpenAPI / Swagger Documentation |
| **Alternative API Docs** | `http://localhost:8000/redoc` | ReDoc API Explorer |
| **System Health Check** | `http://localhost:8000/api/v1/health` | Service & Simulator Status |

---

## 10. Verification & Test Suite Execution

### Running Backend Unit & Security Tests
```powershell
.\venv\Scripts\Activate.ps1
pytest backend/tests -v
# Executes 84 unit and algorithmic tests across classical, quantum, and security suites
```

### Running Frontend Tests & Production Build
```powershell
cd frontend
npm run test
# Executes 15 Vitest component and store tests

npm run build
# Verifies zero-error TypeScript compilation and Vite production bundle creation
cd ..
```

---

## 11. Classical Forensics Techniques & Formulations

1. **Error Level Analysis (ELA):**
   $$\Delta E(x, y) = |I(x, y) - I_{\text{recompress}}(x, y, Q)| \times \alpha$$
   Measures localized high-frequency DCT quantization error disparities.
2. **Noise Variance Inconsistency:**
   $$\sigma_k = \sqrt{\frac{1}{|T_k|-1} \sum_{(x,y) \in T_k} (\nabla^2 I(x,y) - \mu_k)^2}$$
   Estimates high-pass Laplacian noise across $32 \times 32$ tiles to isolate sensor pattern mismatches.
3. **Copy-Move Keypoint Matching:**
   Extracts invariant SIFT/ORB descriptors and identifies spatially displaced duplicates ($\Delta s > 40\text{ px}$) using agglomerative clustering.
4. **CFA Demosaicing Analysis:**
   Analyzes interpolation periodicity in the Fourier spectrum of chromatic residual planes to detect disrupted Bayer array signatures.

---

## 12. Quantum-Assisted Micro-Patch Analysis

Q-TRACE incorporates quantum state representation for micro-patches ($4 \times 4$ and $8 \times 8$ pixels):
1. **Amplitude Encoding:** Maps normalized pixel vectors into pure state vectors:
   $$|\psi\rangle = \sum_{i=0}^{N-1} p_i |i\rangle, \quad \sum |p_i|^2 = 1$$
2. **Quantum State Tomography (QST):** Reconstructs patch density matrices ($\rho$) from simulated projective measurements.
3. **Uhlmann Fidelity & Trace Distance:**
   $$F(\rho_1, \rho_2) = \left(\text{Tr}\sqrt{\sqrt{\rho_1}\rho_2\sqrt{\rho_1}}\right)^2, \quad D(\rho_1, \rho_2) = \frac{1}{2}\text{Tr}|\rho_1 - \rho_2|$$

---

## 13. Scientific Boundary & Quantum Non-Claims Disclosure

> [!NOTE]
> **QUANTUM SIMULATION BOUNDARY**  
> 1. All quantum circuits run on a **local classical CPU simulator** (Qiskit Aer Statevector).  
> 2. Q-TRACE does **NOT** claim quantum computational speedup or exponential acceleration over classical computers.  
> 3. Quantum techniques are applied strictly to **micro-patches** ($4 \times 4$ and $8 \times 8$), exploring representational geometry in Hilbert space rather than full-frame processing.

---

## 14. Key Empirical Benchmark Summary

Evaluated across 120 synthetic automotive collision images:
- **Aggregate Classical Detection:** Precision $88.2\%$, Recall $87.5\%$, F1-Score $0.878$, AUC-ROC $0.932$.
- **Robustness Boundary:** Reliable detection maintained down to $Q \ge 60$ (F1 = $0.78$); sharp degradation below $Q = 50$.
- **Quantum Sensitivity:** Quantum Fidelity demonstrates $+65.0\%$ higher dynamic separation on subtle high-frequency edge shifts compared to normalized Euclidean distance.
- **Coupon Collector Shot Bound:** $4 \times 4$ micro-patch tomography achieves $R^2 > 0.998$ state reconstruction fidelity with $M = 2048$ shots.

---

## 15. Security, Evidence Integrity & Chain-of-Custody

- **Cryptographic Sealing:** SHA-256 computed immediately upon upload prior to parsing.
- **WORM Storage:** Master files stored read-only in `storage/originals/` indexed by UUIDv4.
- **Decompression Bomb Defense:** Capped at $100\text{ MP}$ and $50\text{ MB}$ to prevent RAM exhaustion.
- **Path Traversal Protection:** Absolute path canonicalization with directory jail confinement.
- **Magic-Byte Whitelist:** Physical byte verification for JPEG, PNG, TIFF, and WebP.

---

## 16. Repository Structure

```
quantum-qtrace/
├── backend/                  # FastAPI Core Backend
│   ├── app/
│   │   ├── api/v1/           # REST endpoints (cases, evidence, forensics, canvas, quantum, dossier)
│   │   ├── core/             # Configuration, security, database engines
│   │   ├── models/           # SQLAlchemy database entities
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Classical forensics, quantum simulator, dossier compiler
│   │   └── utils/            # Hashing, image I/O, security sanitizers
│   ├── tests/                # 84 Unit, algorithmic, and security tests
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React 19 + TypeScript + Vite UI
│   ├── src/
│   │   ├── components/       # UI studios (Canvas2D, QuantumLab, Dossier, Evidence)
│   │   ├── stores/           # Zustand state management
│   │   └── types/            # TypeScript interfaces
│   └── package.json          # Node dependencies & test scripts
├── docs/                     # Technical, research & setup documentation
│   ├── ARCHITECTURE.md       # Full architectural specification
│   ├── LOCAL_SETUP.md        # Step-by-step local install runbook
│   ├── USER_GUIDE.md         # Forensic investigator operational manual
│   ├── API_DOCUMENTATION.md  # Complete OpenAPI / REST contract
│   ├── RESEARCH_METHODOLOGY.md # Mathematical formulations & derivations
│   ├── EXPERIMENTS_AND_RESULTS.md # Empirical benchmark tables
│   ├── SECURITY_AND_PRIVACY.md # Threat model & defense implementation
│   └── LIMITATIONS_AND_FUTURE_SCOPE.md # Scientific boundaries & roadmap
├── results/part9/            # Verified benchmark datasets (CSV & JSON)
├── storage/                  # Local WORM storage (originals, derivatives, reports)
├── submission/               # Final Capstone Submission Package
│   ├── PROJECT_REPORT.md     # Academic project report
│   ├── VIVA_NOTES.md         # Oral defense questions & answers
│   └── SUBMISSION_CHECKLIST.md # Audited deliverable verification
└── README.md                 # Primary project overview
```

---

## 17. Configuration & Environment Variables

All settings are managed via `.env` in the repository root:

| Variable | Default Value | Description |
|:---|:---|:---|
| `APP_NAME` | `Q-TRACE Forensic Workstation` | Application display name |
| `APP_VERSION` | `1.0.0` | Production release version |
| `API_V1_STR` | `/api/v1` | REST API prefix |
| `HOST` | `127.0.0.1` | Local loopback binding host |
| `PORT` | `8000` | Backend server port |
| `STORAGE_BASE_DIR` | `./storage` | Master evidence storage root |
| `MAX_UPLOAD_SIZE_BYTES` | `52428800` | Maximum file upload size ($50\text{ MB}$) |
| `QUANTUM_BACKEND` | `aer_simulator_statevector` | Local Qiskit Aer simulation engine |

---

## 18. Scientific Limitations & Future Research

- **Computational Scaling:** CPU statevector simulation scales exponentially; physical QPU dispatch remains the future goal for larger patches.
- **Compression Floor:** Classical detection accuracy degrades sharply on ultra-compressed images ($Q < 50$).
- **Generative Diffusion:** Future work will integrate Vision Transformers (ViT) to improve detection of latent diffusion inpainting.

---

## 19. Academic Credits & Project Information

- **Project Lead & Developer:** Pranav Agarwal ([@agarwalpranav0711](https://github.com/agarwalpranav0711))
- **Institution / Domain:** Final Capstone Project — Digital Image Forensics & Quantum Computing Application
- **Contact:** agarwalpranav0711@gmail.com

---

## 20. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
