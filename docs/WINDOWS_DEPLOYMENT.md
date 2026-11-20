# Q-TRACE Windows Deployment & Standalone Operation Guide

## 1. Local-First Standalone Deployment Philosophy

Q-TRACE is intentionally designed as a zero-cloud, local-first forensic workstation. Digital evidence submitted in motor vehicle insurance disputes frequently contains sensitive personally identifiable information (PII), vehicle identification numbers (VIN), location EXIF tags, and license plates. Transporting evidentiary bitstreams to third-party cloud APIs poses significant chain-of-custody and regulatory liabilities under data protection regulations (GDPR, CCPA) and evidentiary admissibility standards (FRE 902).

Q-TRACE runs entirely within the boundaries of a single Windows workstation, with all compute operations (cryptographic hashing, classical signal processing, quantum circuit simulation, and PDF rendering) executed locally.

---

## 2. Directory Layout & Relational Storage Paths

```text
d:\WebDev PROJECTS\quantum qtrace\
├── backend/                  # FastAPI Application, Services & ORM Models
│   ├── app/
│   │   ├── api/              # REST Endpoints (cases, forensics, canvas, quantum, dossier)
│   │   ├── core/             # Config, Exceptions, Logging, Security
│   │   ├── database/         # SQLite Session Factory, WAL Pragmas
│   │   ├── forensics/        # 7 Classical Forensic Analyzers & Pipeline
│   │   ├── integrations/     # QuantumAdapter & Qiskit simulation bridge
│   │   ├── models/           # SQLAlchemy Data Models (Case, Evidence, ROI, Dossier, Export)
│   │   ├── schemas/          # Pydantic Request/Response Validation Schemas
│   │   ├── services/         # CaseService, CanvasService, DossierService, PDFGenerator
│   │   └── storage/          # StorageService, WORM Vault, Path Traversal Defense
├── frontend/                 # React 18 + Vite + TypeScript Forensic Workstation
│   ├── src/
│   │   ├── components/       # Dark-theme forensic UI primitives & layout
│   │   ├── pages/            # 11 Workstation Screens (Canvas, Reports, Quantum Lab, etc.)
│   │   └── services/         # Centralized typed API client
├── scripts/                  # Automated Windows PowerShell Operations
│   ├── setup.ps1             # One-click environment provisioning
│   ├── launch.ps1            # Multi-process workstation launch & health check
│   ├── test.ps1              # Quality gate runner (102 backend + 15 frontend tests)
│   ├── seed_demo_data.py     # Safe synthetic evidence generator
│   └── reset_demo_data.py    # Isolated synthetic demonstration purger
├── storage/                  # Local WORM Evidence Hierarchy
│   ├── originals/            # Content-addressed read-only source files
│   ├── derivatives/          # Lossless ROI crops & difference heatmaps
│   ├── analysis/             # Classical forensic masks & feature arrays
│   ├── reports/              # Exported PDF and JSON dossiers
│   └── temp/                 # Ephemeral upload buffer
├── qtrace.db                 # SQLite Relational Database (WAL mode enabled)
├── requirements.txt          # Frozen backend dependencies
├── .env                      # Local runtime environment overrides
└── .env.example              # Template configuration
```

---

## 3. PowerShell Security & Execution Policies

If your Windows workstation restricts script execution by default, you can execute the scripts safely without permanently lowering system-wide security:

```powershell
# Execute with per-process execution policy bypass
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\launch.ps1
```

