<#
.SYNOPSIS
    Q-TRACE Environment Setup & Dependency Installation Script for Windows.
.DESCRIPTION
    Validates Python and Node.js runtimes, provisions virtual environments,
    installs backend and frontend dependencies, initializes storage trees,
    and sets up local SQLite database.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Q-TRACE: Quantum-Assisted Digital Image Forensics Platform" -ForegroundColor Cyan
Write-Host "  Automated System Setup & Dependency Installation (Windows)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify Python Installation
Write-Host "`n[1/6] Verifying Python Runtime..." -ForegroundColor Yellow
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Error "Python was not found on PATH. Please install Python 3.11+ from https://www.python.org/"
    exit 1
}
$PythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
Write-Host "  Found Python version: $PythonVersion" -ForegroundColor Green

# 2. Virtual Environment Setup
Write-Host "`n[2/6] Configuring Python Virtual Environment..." -ForegroundColor Yellow
$VenvDir = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenvDir)) {
    Write-Host "  Creating virtual environment at $VenvDir..." -ForegroundColor Gray
    python -m venv $VenvDir
}
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = "python"
}
Write-Host "  Using Python executable: $VenvPython" -ForegroundColor Green

# 3. Install Backend Dependencies
Write-Host "`n[3/6] Installing Backend Dependencies from requirements.txt..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
Write-Host "  Backend dependencies successfully verified." -ForegroundColor Green

# 4. Verify Node.js & Install Frontend Dependencies
Write-Host "`n[4/6] Configuring Frontend Workstation (React + Vite)..." -ForegroundColor Yellow
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
$NpmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $NodeCmd -or -not $NpmCmd) {
    Write-Error "Node.js or npm was not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
}
$NodeVersion = node -v
Write-Host "  Found Node.js version: $NodeVersion" -ForegroundColor Green

Set-Location (Join-Path $ProjectRoot "frontend")
Write-Host "  Installing frontend packages..." -ForegroundColor Gray
npm install
Set-Location $ProjectRoot

# 5. Environment & Storage Initialization
Write-Host "`n[5/6] Initializing Local Configuration & Storage Layout..." -ForegroundColor Yellow
$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "  Created initial .env from template." -ForegroundColor Green
} else {
    Write-Host "  Configuration file .env already present." -ForegroundColor Gray
}

# Ensure storage directories exist
$StorageDirs = @(
    "storage\originals",
    "storage\derivatives",
    "storage\analysis",
    "storage\experiments",
    "storage\reports",
    "storage\temp"
)
foreach ($dir in $StorageDirs) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
}
Write-Host "  Storage hierarchy verified in storage\" -ForegroundColor Green

# 6. Database Initialization
Write-Host "`n[6/6] Initializing SQLite Relational Database..." -ForegroundColor Yellow
& $VenvPython -c "from backend.app.database.session import init_db; init_db(); print('  Database schema initialized in WAL mode.')"

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  Q-TRACE System Setup Complete! Ready to launch." -ForegroundColor Green
Write-Host "  Run: powershell -ExecutionPolicy Bypass -File .\scripts\launch.ps1" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
