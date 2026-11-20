"""Integration tests for Q-TRACE FastAPI endpoints."""

import io
import os
import stat
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.database.session import get_db, Base, engine, SessionLocal
from backend.app.storage.service import get_storage_service, StorageService


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """Test client fixture with isolated SQLite database and storage directory."""
    temp_dir = tmp_path_factory.mktemp("api_test_env")
    test_db = temp_dir / "api_test.db"
    test_storage = temp_dir / "storage"

    # Configure isolated storage service singleton
    custom_storage = StorageService(root_path=test_storage)
    import backend.app.storage.service as storage_module
    storage_module._storage_service = custom_storage

    # Create tables
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client


def create_sample_png(width=64, height=64) -> bytes:
    """Generate in-memory valid PNG image."""
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=(50, 100, 150))
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_root_and_health_endpoints(client: TestClient):
    """Test root and health check endpoints."""
    # Root
    res_root = client.get("/")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert data_root["service"] == "Q-TRACE"

    # Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_v1_health = client.get("/api/v1/health")
    assert res_v1_health.status_code == 200
    assert res_v1_health.json()["status"] == "healthy"


def test_system_info_endpoint(client: TestClient):
    """Test system info endpoint reporting storage, database, and quantum backend."""
    res = client.get("/api/v1/system/info")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["database"]["connected"] is True
    assert data["storage"]["accessible"] is True
    assert data["quantum"]["aer_simulator_available"] is True


def test_case_lifecycle_and_evidence_upload(client: TestClient):
    """Test full workflow: create case -> add note -> upload evidence -> verify integrity."""
    import uuid
    unique_case_num = f"QC-2026-API-{uuid.uuid4().hex[:6].upper()}"

    # 1. Create Case
    case_payload = {
        "case_number": unique_case_num,
        "title": "Suspected Staged Collision Claim",
        "description": "Front-end bumper impact photograph verification.",
    }
    res_create = client.post("/api/v1/cases", json=case_payload)
    assert res_create.status_code == 201
    case_data = res_create.json()
    case_id = case_data["id"]
    assert case_data["case_number"] == unique_case_num
    assert case_data["status"] == "OPEN"

    # Duplicate case_number rejection
    res_dup = client.post("/api/v1/cases", json=case_payload)
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["code"] == "INTEGRITY_VIOLATION"

    # 2. Add Examiner Note
    note_payload = {
        "author": "Examiner Fox",
        "content": "Initial visual review reveals unnatural specular reflection on hood.",
    }
    res_note = client.post(f"/api/v1/cases/{case_id}/notes", json=note_payload)
    assert res_note.status_code == 201
    assert res_note.json()["author"] == "Examiner Fox"

    # 3. Upload Evidence
    png_data = create_sample_png(128, 128)
    files = {"file": ("hood_damage.png", png_data, "image/png")}
    res_upload = client.post(f"/api/v1/cases/{case_id}/evidence", files=files)
    assert res_upload.status_code == 201
    evidence_data = res_upload.json()
    evidence_id = evidence_data["id"]
    assert evidence_data["original_filename"] == "hood_damage.png"
    assert evidence_data["width"] == 128
    assert evidence_data["height"] == 128
    assert evidence_data["status"] == "VERIFIED"
    assert len(evidence_data["sha256_hash"]) == 64

    # 4. Verify Case Details
    res_detail = client.get(f"/api/v1/cases/{case_id}")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["evidence_count"] == 1
    assert len(detail_data["notes"]) == 1

    # 5. Audit Evidence Integrity (Pristine)
    res_verify = client.post(f"/api/v1/evidence/{evidence_id}/verify")
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert verify_data["is_intact"] is True
    assert verify_data["status"] == "VERIFIED"

    # 6. Tamper Simulation and Audit
    stored_path = evidence_data["storage_path"]
    os.chmod(stored_path, stat.S_IWRITE)
    with open(stored_path, "wb") as f:
        f.write(b"TAMPERED_CONTENT_TEST")

    res_tamper_verify = client.post(f"/api/v1/evidence/{evidence_id}/verify")
    assert res_tamper_verify.status_code == 200
    tamper_data = res_tamper_verify.json()
    assert tamper_data["is_intact"] is False
    assert tamper_data["status"] == "COMPROMISED"


def test_not_found_handling(client: TestClient):
    """Ensure non-existent resources return standardized 404 JSON."""
    res = client.get("/api/v1/cases/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
    error_data = res.json()
    assert "error" in error_data
    assert error_data["error"]["code"] == "ENTITY_NOT_FOUND"

