<#
.SYNOPSIS
    Q-TRACE Operational Launch Script for Windows.
.DESCRIPTION
    Starts the FastAPI backend server and Vite frontend development server,
    verifies service health, and displays active workstation URLs.
#>

[CmdletBinding()]
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Q-TRACE: Starting Forensics Workstation & Quantum Lab" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Resolve Python Executable
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = "python"
}

# 1. Start Backend FastAPI Server
Write-Host "`n[1/3] Launching FastAPI Backend on port $BackendPort..." -ForegroundColor Yellow
$BackendJob = Start-Process -FilePath $VenvPython `
    -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $ProjectRoot `
    -PassThru

Write-Host "  Backend process started (PID: $($BackendJob.Id))." -ForegroundColor Gray

# 2. Wait for Backend Health
Write-Host "`n[2/3] Verifying Backend Health..." -ForegroundColor Yellow
$Healthy = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($res.status -eq "healthy") {
            $Healthy = $true
            break
        }
    } catch {
        # Retry until timeout
    }
}

if (-not $Healthy) {
    Write-Error "Backend failed to report healthy status within 15 seconds."
    Stop-Process -Id $BackendJob.Id -Force
    exit 1
}
Write-Host "  Backend verified healthy: http://127.0.0.1:$BackendPort/health" -ForegroundColor Green

# 3. Start Frontend Development Server
Write-Host "`n[3/3] Launching Frontend Forensics Workstation..." -ForegroundColor Yellow
$FrontendDir = Join-Path $ProjectRoot "frontend"
$FrontendJob = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run", "dev" `
    -WorkingDirectory $FrontendDir `
    -PassThru

Write-Host "  Frontend process started (PID: $($FrontendJob.Id))." -ForegroundColor Gray

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  Q-TRACE WORKSTATION IS LIVE & OPERATIONAL" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Forensics Workstation UI: http://localhost:$FrontendPort" -ForegroundColor Cyan
Write-Host "  Core REST API Base:      http://127.0.0.1:$BackendPort/api/v1" -ForegroundColor Cyan
Write-Host "  Interactive OpenAPI Docs: http://127.0.0.1:$BackendPort/docs" -ForegroundColor Cyan
Write-Host "  System Health Check:      http://127.0.0.1:$BackendPort/health" -ForegroundColor Cyan
Write-Host "`n  To stop all services, press Ctrl+C or close this window." -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Green

if (-not $NoBrowser) {
    Start-Process "http://localhost:$FrontendPort"
}

# Keep process alive to monitor child jobs
try {
    while ($true) {
        Start-Sleep -Seconds 2
        if ($BackendJob.HasExited) {
            Write-Warning "Backend process terminated unexpectedly."
            break
        }
        if ($FrontendJob.HasExited) {
            Write-Warning "Frontend process terminated unexpectedly."
            break
        }
    }
} finally {
    Write-Host "`nShutting down Q-TRACE services..." -ForegroundColor Yellow
    if ($BackendJob -and -not $BackendJob.HasExited) { Stop-Process -Id $BackendJob.Id -Force }
    if ($FrontendJob -and -not $FrontendJob.HasExited) { Stop-Process -Id $FrontendJob.Id -Force }
    Write-Host "All processes cleanly stopped." -ForegroundColor Green
}
