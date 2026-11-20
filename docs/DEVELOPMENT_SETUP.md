# Q-TRACE Developer Setup & Local Operational Guide

## 1. System Requirements

The Q-TRACE platform is designed for local-first execution without requiring external database daemons, Docker, or dedicated GPU hardware.

- **Operating System**: Windows 10/11 (64-bit), Ubuntu 22.04+ LTS, or macOS 13+ (Ventura or later).
- **Python**: Version **3.11.x** (recommended) or 3.10+.
- **Node.js**: Version **v20+** / **v22+** (required for upcoming frontend in Part 4).
- **RAM**: Minimum 8 GB (16 GB recommended for concurrent quantum circuit simulation).
- **Disk**: 2 GB free SSD space for database, evidence storage, and simulation logs.

---

## 2. Environment Configuration

### 2.1 Clone Repository and Enter Directory
```powershell
cd "d:\WebDev PROJECTS\quantum qtrace"
```

### 2.2 Python Virtual Environment
Activate your existing Python virtual environment or create a fresh one:
```powershell
# Create venv (if not already existing)
python -m venv venv

# Activate venv on Windows PowerShell
.\venv\Scripts\Activate.ps1
```

### 2.3 Dependency Verification
Ensure all required Python packages are installed:
```powershell
python -m pip install qiskit qiskit-aer scipy numpy matplotlib opencv-python pytest fastapi uvicorn pydantic pydantic-settings sqlalchemy httpx python-multipart pillow
```

### 2.4 Environment Variables Template
Copy the configuration template `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Key configuration options in `.env`:
- `DATABASE_URL`: `sqlite:///./qtrace.db` (Default SQLite database path).
- `STORAGE_ROOT`: `./storage` (Evidence preservation directory).
- `MAX_UPLOAD_BYTES`: `52428800` (50 MB upload boundary).
- `LOG_LEVEL`: `INFO` (Console logging granularity: `DEBUG`, `INFO`, `WARNING`, `ERROR`).
- `PORT`: `8000` (FastAPI listening port).

---

## 3. Running the Q-TRACE Backend Server

Start the FastAPI application with live auto-reload enabled:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected startup log output:
```text
2026-11-19 21:00:00 | INFO    | qtrace.main:lifespan:28 - Starting Q-TRACE v0.3.0 [development]
2026-11-19 21:00:00 | INFO    | qtrace.database:init_db:43 - Initializing database schema...
2026-11-19 21:00:00 | INFO    | qtrace.database:init_db:47 - Database schema initialized successfully.
2026-11-19 21:00:00 | INFO    | qtrace.main:lifespan:35 - Storage subsystem ready at D:\WebDev PROJECTS\quantum qtrace\storage
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Once running:
- **Interactive OpenAPI Docs (Swagger UI)**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.
- **ReDoc Documentation**: Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).
- **Health Check**: Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

---

## 4. Running Automated Tests

Q-TRACE maintains an automated regression and integration test suite covering both Part 2 quantum algorithms and Part 3 backend subsystems.

### 4.1 Run Complete Test Suite (79 Tests)
```powershell
python -m pytest tests -v
```

### 4.2 Run Specific Subsystem Test Suites
```powershell
# Backend Storage & WORM Security Tests
python -m pytest tests/test_backend_storage.py -v

# Cryptographic SHA-256 Integrity Tests
python -m pytest tests/test_backend_integrity.py -v

# Image Validation & Magic Byte Security Tests
python -m pytest tests/test_backend_validation.py -v

# SQLite Database & ORM Model Tests
python -m pytest tests/test_backend_database.py -v

# FastAPI REST Endpoints & Integrity Audit Tests
python -m pytest tests/test_backend_api.py -v

# Quantum API Simulation Integration Tests
python -m pytest tests/test_backend_quantum_integration.py -v

# Quantum End-to-End Simulation Tests (Part 2 Baseline)
python -m pytest tests/test_end_to_end.py -v
```

---

## 5. Database Reset Procedure

To reset the database to a clean baseline state:
```powershell
# Stop any running uvicorn process, then delete SQLite database and WAL files
Remove-Item -Force qtrace.db, qtrace.db-wal, qtrace.db-shm -ErrorAction SilentlyContinue

# The database tables will be re-created automatically on next server launch
```

