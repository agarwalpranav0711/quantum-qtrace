"""API integration tests for classical forensic pipeline and artifact endpoints."""

import io
import uuid
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.models.evidence import Evidence
from backend.app.storage.service import StorageService
import backend.app.storage.service as storage_module


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """TestClient fixture with isolated storage directory and tables."""
    temp_dir = tmp_path_factory.mktemp("forensic_api_env")
    test_storage = temp_dir / "storage"

    custom_storage = StorageService(root_path=test_storage)
    storage_module._storage_service = custom_storage

    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client


def create_test_jpeg(width=128, height=128) -> bytes:
    """Generate in-memory test JPEG image."""
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=(140, 150, 160))
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def test_list_forensic_techniques_endpoint(client: TestClient):
    """Test GET /api/v1/forensics/techniques returns all registered algorithms."""
    res = client.get("/api/v1/forensics/techniques")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 7

    technique_ids = [t["id"] for t in data]
    assert "metadata" in technique_ids
    assert "ela" in technique_ids
    assert "noise" in technique_ids
    assert "copy_move" in technique_ids
    assert "statistics" in technique_ids
    assert "perceptual_hash" in technique_ids
    assert "resampling" in technique_ids


def test_full_forensic_pipeline_execution(client: TestClient):
    """
    Test uploading evidence, executing forensic analysis, verifying database persistence,
    checking WORM evidence immutability, and streaming generated artifacts.
    """
    # 1. Ingest Evidence
    image_bytes = create_test_jpeg(128, 128)
    upload_res = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("test_car.jpg", image_bytes, "image/jpeg")},
    )
    assert upload_res.status_code == 201
    evidence_data = upload_res.json()
    evidence_id = evidence_data["id"]
    original_sha256 = evidence_data["sha256_hash"]

    # 2. Execute Forensic Analysis Suite (run metadata, ela, noise, statistics)
    analyze_payload = {
        "techniques": ["metadata", "ela", "noise", "statistics", "perceptual_hash", "resampling"],
        "parameters": {
            "ela": {"quality": 95, "scale": 15},
            "noise": {"block_size": 16},
        },
    }
    analyze_res = client.post(
        f"/api/v1/evidence/{evidence_id}/analyze",
        json=analyze_payload,
    )
    assert analyze_res.status_code == 200
    summary = analyze_res.json()

    assert summary["evidence_id"] == evidence_id
    assert summary["status"] == "COMPLETED"
    assert summary["techniques_run"] == 6
    assert summary["techniques_succeeded"] >= 5
    assert len(summary["artifacts"]) >= 3

    analysis_id = summary["analysis_id"]

    # 3. Verify WORM Immutability: original evidence file SHA-256 must NOT have changed
    verify_res = client.post(f"/api/v1/evidence/{evidence_id}/verify")
    assert verify_res.status_code == 200
    assert verify_res.json()["is_intact"] is True
    assert verify_res.json()["current_sha256"] == original_sha256

    # 4. Fetch Analysis by ID
    get_res = client.get(f"/api/v1/analysis/{analysis_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["analysis_id"] == analysis_id
    assert "ela" in retrieved["technique_results"]

    # 5. List Analyses for Evidence
    list_res = client.get(f"/api/v1/evidence/{evidence_id}/analyses")
    assert list_res.status_code == 200
    hist = list_res.json()
    assert len(hist) >= 1
    assert hist[0]["analysis_id"] == analysis_id

    # 6. Stream Generated Artifact Binary File
    first_artifact = summary["artifacts"][0]
    art_id = first_artifact["artifact_id"]
    stream_res = client.get(f"/api/v1/analysis/{analysis_id}/artifacts/{art_id}/file")
    assert stream_res.status_code == 200
    assert stream_res.headers["content-type"] == "image/png"
    assert len(stream_res.content) > 0


def test_analyze_invalid_evidence_id(client: TestClient):
    """Test analyzing non-existent evidence returns 404."""
    fake_id = str(uuid.uuid4())
    res = client.post(
        f"/api/v1/evidence/{fake_id}/analyze",
        json={"techniques": ["metadata"]},
    )
    assert res.status_code == 404

