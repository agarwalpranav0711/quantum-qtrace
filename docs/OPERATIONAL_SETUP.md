# Q-TRACE Operational Setup & Quickstart Guide

## 1. Prerequisites & System Requirements

- **Operating System:** Windows 10 / Windows 11 (64-bit)
- **Python Version:** Python 3.11+ (Python 3.11.9 recommended)
- **Node.js Version:** Node.js 18+ LTS (Node v20+ / v22+ verified)
- **Memory (RAM):** 8 GB minimum (16 GB recommended for high-resolution images)
- **Disk Storage:** 2 GB free disk space for dependencies and local evidence storage
- **Hardware Acceleration:** None required (Runs entirely on standard CPU; no GPU or quantum hardware needed)

---

## 2. One-Time Setup Procedure

Open Windows PowerShell in the project root directory and execute:

```powershell
# 1. Run the automated environment setup script
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### What `setup.ps1` does automatically:
1. Verifies Python 3.11+ is accessible on PATH.
2. Creates a local Python virtual environment in `.venv/`.
3. Installs backend dependencies from `requirements.txt`.
4. Installs frontend dependencies in `frontend/node_modules/` via npm.
5. Provisions local `.env` configuration file from `.env.example`.
6. Initializes the `storage/` directory hierarchy (`originals`, `derivatives`, `analysis`, `reports`, `temp`).
7. Initializes the SQLite database in Write-Ahead Logging (WAL) mode.

---

## 3. Starting the Application

```powershell
# Launch both backend and frontend servers
powershell -ExecutionPolicy Bypass -File .\scripts\launch.ps1
```

The script will launch:
1. **FastAPI Backend Server**: Running at `http://127.0.0.1:8000`
2. **Frontend Workstation**: Running at `http://localhost:5173`
3. Automatically performs a health check against `/health` before launching the browser.

---

## 4. Running the Master Test Suite

```powershell
# Execute full quality assurance and regression test suite
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Runs:
- Backend Pytest suite (**102 tests**)
- Frontend Vitest suite (**15 tests**)
- Frontend production build verification (`tsc -b && vite build`)

