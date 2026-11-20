# Q-TRACE Diagnostics, Logging & Troubleshooting Guide

## 1. System Diagnostics Architecture

Q-TRACE provides centralized diagnostic endpoints and structured logging across all core subsystems:
- **Root Health Check:** `GET /health` (Returns service operational status, version, and project metadata)
- **Deep System Diagnostics:** `GET /api/v1/system/info` (Queries SQLite WAL pragma status, storage directory availability, and Qiskit quantum simulator capabilities)
- **Interactive OpenAPI Specification:** `GET /docs` and `GET /redoc`

---

## 2. Common Issues & Resolution Playbook

### Issue 1: Port 8000 or 5173 Already in Use
- **Symptom:** Backend or frontend fails to start with `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): address already in use`.
- **Diagnosis:** A previous instance of Uvicorn or Node is still running in the background.
- **Resolution:**
  ```powershell
  # Find and terminate process occupying port 8000 on Windows
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  # Launch with custom ports
  powershell -ExecutionPolicy Bypass -File .\scripts\launch.ps1 -BackendPort 8080 -FrontendPort 3000
  ```

### Issue 2: Storage Permission Error on File Upload or Reset
- **Symptom:** `PermissionError: [WinError 5] Access is denied` when trying to modify or delete an original evidence file in `storage/originals/`.
- **Diagnosis:** Q-TRACE enforces WORM preservation by applying `stat.S_IREAD` (read-only NTFS permissions) to all ingested original evidence.
- **Resolution:** This is the expected security behavior. Original evidence must never be manually modified. To safely remove synthetic demonstration files, use `python scripts/reset_demo_data.py`, which handles temporary permission lifting safely.

### Issue 3: PowerShell Script Execution Policy Blocked
- **Symptom:** `File ... cannot be loaded because running scripts is disabled on this system.`
- **Diagnosis:** Windows PowerShell default execution policy is `Restricted`.
- **Resolution:** Run with the bypass parameter:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
  ```

### Issue 4: Missing Virtual Environment Dependencies
- **Symptom:** `ModuleNotFoundError: No module named 'reportlab'` or `No module named 'qiskit'`.
- **Diagnosis:** Active shell is using system global Python rather than the project virtual environment.
- **Resolution:**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

## 3. Log Output Format & Privacy Shielding

Logs use structured format:
`YYYY-MM-DD HH:MM:SS | LEVEL | module:function:line - Message`
- **Zero Evidence Leakage:** Binary image data and base64 strings are never logged to console or disk.
- **Sanitized Filenames:** Only SHA-256 digests and sanitized filenames are recorded in log messages.

