"""Integration tests for quantum comparison API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    """Test client fixture."""
    with TestClient(app) as c:
        yield c


def test_quantum_compare_identical_patches_16q(client: TestClient):
    """Test quantum comparison on identical 4x4 patches using 16-qubit architecture."""
    patch = [
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
        [130, 140, 150, 160],
    ]
    payload = {
        "patch_a": patch,
        "patch_b": patch,
        "architecture": "16q",
        "shots": 200,
    }
    response = client.post("/api/v1/quantum/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["architecture"] == "16q"
    assert data["qubits"] == 16
    assert data["identical"] is True
    assert data["difference_count"] == 0
    assert data["fidelity"] >= 0.99
    assert data["shots_used"] == 200


def test_quantum_compare_different_patches_12q(client: TestClient):
    """Test quantum comparison on differing 4x4 patches using 12-qubit architecture."""
    patch_a = [
        [0, 0, 0, 0],
        [0, 100, 100, 0],
        [0, 100, 100, 0],
        [0, 0, 0, 0],
    ]
    patch_b = [
        [0, 0, 0, 0],
        [0, 200, 100, 0],  # Single pixel altered at (1, 1)
        [0, 100, 100, 0],
        [0, 0, 0, 0],
    ]
    payload = {
        "patch_a": patch_a,
        "patch_b": patch_b,
        "architecture": "12q",
        "shots": 300,
    }
    response = client.post("/api/v1/quantum/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["architecture"] == "12q"
    assert data["qubits"] == 12
    assert data["identical"] is False
    assert data["difference_count"] >= 1
    assert data["reconstructed_diff_map"][1][1] != 0


def test_quantum_compare_validation_error_dimensions(client: TestClient):
    """Ensure invalid patch dimensions (not 4x4) are rejected with 422."""
    payload = {
        "patch_a": [[1, 2], [3, 4]],  # 2x2 instead of 4x4
        "patch_b": [[1, 2], [3, 4]],
        "architecture": "16q",
    }
    response = client.post("/api/v1/quantum/compare", json=payload)
    assert response.status_code == 422


def test_quantum_compare_validation_error_pixel_range(client: TestClient):
    """Ensure out-of-range pixel values (> 255) are rejected with 422."""
    bad_patch = [
        [300, 0, 0, 0],  # 300 > 255
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    payload = {
        "patch_a": bad_patch,
        "patch_b": bad_patch,
        "architecture": "16q",
    }
    response = client.post("/api/v1/quantum/compare", json=payload)
    assert response.status_code == 422

