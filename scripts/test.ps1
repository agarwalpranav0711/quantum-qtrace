<#
.SYNOPSIS
    Q-TRACE Master Automated Verification & Test Runner for Windows.
.DESCRIPTION
    Executes backend Pytest suite, frontend Vitest component tests,
    and frontend production compilation.
#>

[CmdletBinding()]
param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Q-TRACE Automated Quality Assurance & Test Verification" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = "python"
}

# 1. Run Backend Tests
if (-not $FrontendOnly) {
    Write-Host "`n[1/3] Running Backend Pytest Test Suite..." -ForegroundColor Yellow
    & $VenvPython -m pytest tests -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Backend test suite failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }
    Write-Host "  Backend test suite passed 100%!" -ForegroundColor Green
}

# 2. Run Frontend Tests
if (-not $BackendOnly) {
    Write-Host "`n[2/3] Running Frontend Vitest Test Suite..." -ForegroundColor Yellow
    Set-Location (Join-Path $ProjectRoot "frontend")
    npm run test
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Frontend test suite failed with exit code $LASTEXITCODE."
        Set-Location $ProjectRoot
        exit $LASTEXITCODE
    }
    Write-Host "  Frontend test suite passed 100%!" -ForegroundColor Green

    # 3. Frontend Production Build Check
    Write-Host "`n[3/3] Verifying Frontend Production Build (tsc + vite build)..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Frontend production build failed with exit code $LASTEXITCODE."
        Set-Location $ProjectRoot
        exit $LASTEXITCODE
    }
    Write-Host "  Frontend production build succeeded cleanly!" -ForegroundColor Green
    Set-Location $ProjectRoot
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  ALL SYSTEM TESTS & BUILD CHECKS PASSED (100% SUCCESS)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
