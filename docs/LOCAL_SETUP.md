# Q-TRACE: Local Setup & Installation Runbook

**Document Reference:** `docs/LOCAL_SETUP.md`  
**Classification:** Operational Installation & Setup Guide  
**Version:** 1.10.0 (Part 10 Final Submission)  

---

## 1. System Prerequisites

Q-TRACE runs completely offline on a standard personal computer. No cloud accounts, external GPUs, or paid APIs are required.

### Hardware & Software Requirements:
- **Operating System:** Windows 10 / 11 (64-bit).
- **Python:** Python 3.11.x (Python 3.11.9 recommended).
- **Node.js:** Node.js v18.x or v20+ with npm (v22.x verified).
- **RAM:** Minimum 8 GB RAM (16 GB recommended).
- **Storage:** Minimum 2 GB free disk space.
- **Terminal:** Windows PowerShell 5.1+ or PowerShell 7+.

---

## 2. Step-by-Step Installation

### Step 1: Clone or Open Repository
```powershell
cd "d:\WebDev PROJECTS\quantum qtrace"
```

### Step 2: Configure Environment Variables
Copy the template configuration file to `.env`:
```powershell
Copy-Item .env.example .env
```
*Note: The default `.env.example` settings are pre-configured for local execution on `127.0.0.1:8000` with zero secrets needed.*

### Step 3: Set Up Python Virtual Environment
```powershell
# Create virtual environment named .venv
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## 3. Automated Setup Script

Alternatively, you can run the included automated setup script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```
This script automatically:
1. Validates Python and Node.js versions.
2. Creates the Python virtual environment and installs `requirements.txt`.
3. Runs `npm install` in the `frontend/` directory.
4. Generates `.env` from `.env.example` if missing.
5. Initializes storage directories with `.gitkeep` markers.

---

## 4. Starting the Application

### Option A: One-Click Operational Launch Script
```powershell
powershell -ExecutionPolicy Bypass -File scripts\launch.ps1
```
This script launches the FastAPI backend on port 8000, launches the Vite frontend on port 5173, verifies service health, and opens the workstation in your default web browser (`http://localhost:5173`).

### Option B: Manual Two-Terminal Launch

**Terminal 1 (Backend Core API):**
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Core API: `http://127.0.0.1:8000`
- Swagger UI Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

**Terminal 2 (Frontend Workstation):**
```powershell
cd frontend
npm run dev
```
- Workstation URL: `http://localhost:5173`

---

## 5. Stopping the Application
- Press `Ctrl + C` in both terminal windows to gracefully terminate uvicorn and Vite processes.
- If background processes persist on Windows, execute:
```powershell
Get-Process -Name python, node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*qtrace*" } | Stop-Process -Force
```

---

## 6. Troubleshooting & Diagnostics

| Symptom | Probable Cause | Exact Solution |
| :--- | :--- | :--- |
| `Execution_Policies` script error | PowerShell restricts unsigned scripts | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| Port 8000 already in use | Previous uvicorn server running | Run `Get-NetTCPConnection -LocalPort 8000` and stop the corresponding PID |
| Port 5173 already in use | Previous Vite server running | Run `npx kill-port 5173` or launch Vite on alternate port |
| `ModuleNotFoundError: backend` | Python path does not include project root | Ensure you run commands from the project root or execute with `python -m` |
| `sqlite3.OperationalError: database locked` | Concurrency lock on `qtrace.db` | Verify SQLite WAL mode is enabled; ensure no locked external database browser is open |
