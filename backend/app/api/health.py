"""Health check and system diagnostic endpoints."""

import sys
import platform
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import qiskit

from backend.app.core.config import get_settings, Settings
from backend.app.database.session import get_db
from backend.app.schemas.health import (
    HealthResponse,
    SystemInfoResponse,
    DatabaseStatus,
    StorageStatus,
    QuantumBackendStatus,
)
from backend.app.storage.service import get_storage_service

router = APIRouter(tags=["Health & System"])


@router.get("/health", response_model=HealthResponse)
def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Basic service health check."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        project=settings.PROJECT_NAME,
    )


@router.get("/system/info", response_model=SystemInfoResponse)
def get_system_info(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SystemInfoResponse:
    """Detailed diagnostics of database, storage, and quantum simulation subsystem."""
    # 1. Database check
    db_connected = False
    wal_enabled = False
    dialect_name = "unknown"
    try:
        dialect_name = db.bind.dialect.name
        result = db.execute(text("PRAGMA journal_mode;")).scalar()
        if result and str(result).lower() == "wal":
            wal_enabled = True
        db_connected = True
    except Exception:
        db_connected = False

    # 2. Storage check
    storage = get_storage_service()
    storage_accessible = storage.root.exists() and storage.root.is_dir()
    dirs_verified = all(
        (storage.root / sub).exists()
        for sub in ["originals", "derivatives", "analysis", "experiments", "reports", "temp"]
    )

    # 3. Quantum Simulator check
    aer_available = False
    try:
        from qiskit_aer import AerSimulator
        aer_available = True
        default_backend = "AerSimulator (Statevector / Matrix Product State)"
    except ImportError:
        default_backend = "Qiskit BasicSimulator (Fallback)"

    return SystemInfoResponse(
        status="operational",
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        python_version=sys.version.split()[0],
        platform=f"{platform.system()} {platform.release()}",
        database=DatabaseStatus(
            connected=db_connected,
            dialect=dialect_name,
            wal_mode=wal_enabled,
        ),
        storage=StorageStatus(
            root_path=str(storage.root),
            accessible=storage_accessible,
            directories_verified=dirs_verified,
        ),
        quantum=QuantumBackendStatus(
            qiskit_version=qiskit.__version__,
            aer_simulator_available=aer_available,
            default_backend=default_backend,
        ),
    )

