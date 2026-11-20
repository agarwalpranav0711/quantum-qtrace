"""Health and system diagnostic schemas."""

from typing import Dict, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str
    version: str
    project: str


class StorageStatus(BaseModel):
    """Storage subsystem status."""
    root_path: str
    accessible: bool
    directories_verified: bool


class QuantumBackendStatus(BaseModel):
    """Quantum simulator status."""
    qiskit_version: str
    aer_simulator_available: bool
    default_backend: str


class DatabaseStatus(BaseModel):
    """Database subsystem status."""
    connected: bool
    dialect: str
    wal_mode: bool


class SystemInfoResponse(BaseModel):
    """Detailed system diagnostic status."""
    status: str
    project_name: str
    version: str
    environment: str
    python_version: str
    platform: str
    database: DatabaseStatus
    storage: StorageStatus
    quantum: QuantumBackendStatus

