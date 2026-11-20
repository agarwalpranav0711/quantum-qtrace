"""Integration tests for Forensic Canvas, ROI management, derived crops, and image comparison."""

import io
import uuid
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
import numpy as np

from backend.app.main import app
from backend.app.database.session import Base, engine
from backend.app.storage.service import StorageService
import backend.app.storage.service as storage_module


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """TestClient fixture with isolated storage directory and tables."""
    temp_dir = tmp_path_factory.mktemp("canvas_api_env")
    test_storage = temp_dir / "storage"

    custom_storage = StorageService(root_path=test_storage)
    storage_module._storage_service = custom_storage

    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client


def make_test_image(width=200, height=150, color=(120, 140, 160)) -> bytes:
    """Generate in-memory test image."""
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 80, 80], fill=(220, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def test_roi_crud_lifecycle(client: TestClient):
    """Test full CRUD lifecycle for Regions of Interest (ROIs)."""
    # 1. Ingest Evidence
    img_bytes = make_test_image(200, 150)
    upload_res = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("car_front.jpg", img_bytes, "image/jpeg")},
    )
    assert upload_res.status_code == 201
    evidence_id = upload_res.json()["id"]

    # 2. Create ROI
    roi_payload = {
        "roi_label": "Dent Cloned Area",
        "roi_type": "EXAMINER_CREATED",
        "x": 20,
        "y": 20,
        "width": 60,
        "height": 60,
        "color": "#00F2FE",
        "observation": "Localized surface indentation with circular geometry",
        "hypothesis": "Possible stamp tool replication from adjacent panel",
        "confidence": 0.85,
    }
    create_res = client.post(
        f"/api/v1/evidence/{evidence_id}/rois",
        json=roi_payload,
    )
    assert create_res.status_code == 201
    roi_data = create_res.json()
    roi_id = roi_data["id"]
    assert roi_data["roi_label"] == "Dent Cloned Area"
    assert roi_data["x"] == 20
    assert roi_data["width"] == 60
    assert roi_data["confidence"] == 0.85

    # 3. List ROIs for Evidence
    list_res = client.get(f"/api/v1/evidence/{evidence_id}/rois")
    assert list_res.status_code == 200
    rois = list_res.json()
    assert len(rois) == 1
    assert rois[0]["id"] == roi_id

    # 4. Get ROI Details
    get_res = client.get(f"/api/v1/rois/{roi_id}")
    assert get_res.status_code == 200
    assert get_res.json()["roi_label"] == "Dent Cloned Area"

    # 5. Update ROI
    update_res = client.patch(
        f"/api/v1/rois/{roi_id}",
        json={"roi_label": "Confirmed Dent Region", "confidence": 0.95},
    )
    assert update_res.status_code == 200
    assert update_res.json()["roi_label"] == "Confirmed Dent Region"
    assert update_res.json()["confidence"] == 0.95

    # 6. Generate ROI Crop Artifact
    crop_res = client.post(f"/api/v1/rois/{roi_id}/crop")
    assert crop_res.status_code == 201
    crop_data = crop_res.json()
    assert crop_data["roi_id"] == roi_id
    assert crop_data["crop_width"] == 60
    assert crop_data["crop_height"] == 60
    assert len(crop_data["sha256_hash"]) == 64
    assert len(crop_data["suggested_quantum_patch"]) == 4
    assert len(crop_data["suggested_quantum_patch"][0]) == 4

    # 7. Stream Derived Crop Artifact
    artifact_id = crop_data["artifact_id"]
    stream_res = client.get(f"/api/v1/derivatives/{artifact_id}/file")
    assert stream_res.status_code == 200
    assert stream_res.headers["content-type"] == "image/png"
    assert len(stream_res.content) > 0

    # 8. Delete ROI
    del_res = client.delete(f"/api/v1/rois/{roi_id}")
    assert del_res.status_code == 204

    # 9. Verify ROI is deleted
    assert client.get(f"/api/v1/rois/{roi_id}").status_code == 404


def test_roi_boundary_validation(client: TestClient):
    """Test coordinate boundary checking and rejection of out-of-bounds selections."""
    img_bytes = make_test_image(100, 100)
    upload_res = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("small.jpg", img_bytes, "image/jpeg")},
    )
    assert upload_res.status_code == 201
    ev_id = upload_res.json()["id"]

    # Origin outside image
    res_outside = client.post(
        f"/api/v1/evidence/{ev_id}/rois",
        json={"roi_label": "Invalid", "x": 150, "y": 150, "width": 20, "height": 20},
    )
    assert res_outside.status_code in [400, 422]

    # Overlapping boundary gets clamped
    res_clamp = client.post(
        f"/api/v1/evidence/{ev_id}/rois",
        json={"roi_label": "Clamped", "x": 80, "y": 80, "width": 50, "height": 50},
    )
    assert res_clamp.status_code == 201
    assert res_clamp.json()["width"] == 20  # 100 - 80 = 20
    assert res_clamp.json()["height"] == 20


def test_image_comparison_identical_and_differing(client: TestClient):
    """Test image comparison between identical pair and differing pair."""
    # Ingest Image 1
    bytes1 = make_test_image(150, 150, color=(100, 100, 100))
    res1 = client.post("/api/v1/evidence/upload", files={"file": ("img1.jpg", bytes1, "image/jpeg")})
    id1 = res1.json()["id"]

    # Ingest Identical Image 2 (same bytes)
    res2 = client.post("/api/v1/evidence/upload", files={"file": ("img2.jpg", bytes1, "image/jpeg")})
    id2 = res2.json()["id"]

    # Ingest Modified Image 3 (different color)
    bytes3 = make_test_image(150, 150, color=(200, 200, 200))
    res3 = client.post("/api/v1/evidence/upload", files={"file": ("img3.jpg", bytes3, "image/jpeg")})
    id3 = res3.json()["id"]

    # 1. Compare Identical
    cmp_ident = client.post(
        "/api/v1/evidence/compare",
        json={"primary_evidence_id": id1, "comparison_evidence_id": id2, "difference_threshold": 10},
    )
    assert cmp_ident.status_code == 200
    data_ident = cmp_ident.json()
    assert data_ident["identical_dimensions"] is True
    assert data_ident["difference_pixel_count"] == 0
    assert data_ident["mean_absolute_error"] == 0.0
    assert data_ident["ssim_score"] >= 0.999
    assert data_ident["artifact_id"] is not None

    # 2. Compare Differing
    cmp_diff = client.post(
        "/api/v1/evidence/compare",
        json={"primary_evidence_id": id1, "comparison_evidence_id": id3, "difference_threshold": 10},
    )
    assert cmp_diff.status_code == 200
    data_diff = cmp_diff.json()
    assert data_diff["difference_pixel_count"] > 100
    assert data_diff["mean_absolute_error"] > 50.0
    assert len(data_diff["suggested_quantum_patch_a"]) == 4
    assert len(data_diff["suggested_quantum_patch_b"]) == 4


def test_compare_nonexistent_evidence(client: TestClient):
    """Test comparison with non-existent UUIDs returns 404."""
    fake_id = str(uuid.uuid4())
    res = client.post(
        "/api/v1/evidence/compare",
        json={"primary_evidence_id": fake_id, "comparison_evidence_id": fake_id},
    )
    assert res.status_code == 404
