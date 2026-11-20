"""Automated tests for forensic investigation dossiers, preview, and ReportLab PDF/JSON exports."""

import io
import json
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.core.config import get_settings
from backend.app.database.session import Base, engine

settings = get_settings()


@pytest.fixture(scope="module")
def client():
    """Module-level test client with database schema created."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def _create_sample_case_and_evidence(client_inst: TestClient):
    """Helper to create a case with uploaded evidence and examiner notes."""
    import uuid
    case_num = f"QC-DOS-{uuid.uuid4().hex[:8].upper()}"

    # 1. Create Case
    res_case = client_inst.post(
        "/api/v1/cases",
        json={
            "case_number": case_num,
            "title": "Rear Bumper Splicing Investigation",
            "description": "Photographic damage claim audit for suspicious fracture edges.",
        },
    )
    assert res_case.status_code in [200, 201]
    case_data = res_case.json()
    case_id = case_data["id"]

    # 2. Add Examiner Note
    res_note = client_inst.post(
        f"/api/v1/cases/{case_id}/notes",
        json={
            "author": "Lead Examiner Miller",
            "content": "Initial visual review indicates unnatural gradient boundaries across rear bumper.",
        },
    )
    assert res_note.status_code in [200, 201]

    # 3. Create dummy 80x60 evidence image
    from PIL import Image
    import io

    img = Image.new("RGB", (80, 60), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    res_upload = client_inst.post(
        "/api/v1/evidence/upload",
        files={"file": ("claim_bumper.jpg", buf, "image/jpeg")},
        data={"case_id": case_id},
    )
    assert res_upload.status_code in [200, 201]
    evidence_id = res_upload.json()["id"]

    # 4. Create an ROI on this evidence
    res_roi = client_inst.post(
        f"/api/v1/evidence/{evidence_id}/rois",
        json={
            "roi_label": "Bumper Crack Anomaly",
            "roi_type": "EXAMINER_CREATED",
            "x": 10,
            "y": 10,
            "width": 20,
            "height": 20,
            "color": "#00F2FE",
            "observation": "High frequency edge transition inconsistent with body seam.",
            "hypothesis": "Possible digital brush or inpainting splice.",
            "confidence": 0.90,
        },
    )
    assert res_roi.status_code in [200, 201]
    roi_data = res_roi.json()

    # 5. Generate sub-region crop artifact
    res_crop = client_inst.post(f"/api/v1/rois/{roi_data['id']}/crop")
    assert res_crop.status_code in [200, 201]

    return case_id, evidence_id, roi_data["id"]


def test_dossier_crud_and_sections(client):
    """Verify dossier creation, default section population, updates, and retrieval."""
    case_id, evidence_id, roi_id = _create_sample_case_and_evidence(client)

    # 1. Create Dossier
    payload = {
        "title": "Formal Forensic Dossier: Claim Rear Bumper",
        "author": "Senior Inspector Vance",
        "confidentiality_level": "STRICTLY CONFIDENTIAL",
        "investigation_scope": "Evaluation of photographic claim integrity and potential localized splicing.",
        "executive_summary": "Photographic evidence was audited across cryptographic and algorithmic pipelines.",
        "examiner_conclusions": "Observed anomalies warrant secondary physical verification.",
        "selected_evidence_ids": [evidence_id],
        "selected_roi_ids": [roi_id],
    }

    res_create = client.post(f"/api/v1/cases/{case_id}/dossiers", json=payload)
    assert res_create.status_code == 201
    dossier = res_create.json()

    assert dossier["title"] == payload["title"]
    assert dossier["author"] == "Senior Inspector Vance"
    assert dossier["status"] == "DRAFT"
    assert dossier["version"] == 1
    assert "DOS-QC-DOS-" in dossier["dossier_number"]
    assert len(dossier["sections"]) == 13

    dossier_id = dossier["id"]

    # 2. Get Dossier
    res_get = client.get(f"/api/v1/dossiers/{dossier_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == dossier_id

    # 3. Update Dossier
    res_update = client.patch(
        f"/api/v1/dossiers/{dossier_id}",
        json={
            "title": "Updated Forensic Dossier: Final Edition",
            "status": "IN_REVIEW",
            "recommendations": "Request raw camera memory card for bitstream verification.",
        },
    )
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["title"] == "Updated Forensic Dossier: Final Edition"
    assert updated["status"] == "IN_REVIEW"
    assert "Request raw camera" in updated["recommendations"]

    # 4. Update Section
    first_sec = dossier["sections"][0]
    res_sec_update = client.patch(
        f"/api/v1/dossiers/{dossier_id}/sections/{first_sec['id']}",
        json={"title": "Primary Incident Identification"},
    )
    assert res_sec_update.status_code == 200
    assert res_sec_update.json()["title"] == "Primary Incident Identification"

    # 5. List Case Dossiers
    res_list = client.get(f"/api/v1/cases/{case_id}/dossiers")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1


def test_dossier_preview_compilation(client):
    """Verify structured dossier preview aggregates evidence, custody, findings, and ROIs."""
    case_id, evidence_id, roi_id = _create_sample_case_and_evidence(client)

    # Create dossier
    res_create = client.post(
        f"/api/v1/cases/{case_id}/dossiers",
        json={"title": "Preview Compilation Audit Dossier"},
    )
    dossier_id = res_create.json()["id"]

    # Preview
    res_prev = client.get(f"/api/v1/dossiers/{dossier_id}/preview")
    assert res_prev.status_code == 200
    preview = res_prev.json()

    assert preview["dossier_id"] == dossier_id
    assert preview["case_id"] == case_id
    assert len(preview["evidence_register"]) >= 1
    assert len(preview["chain_of_custody_events"]) >= 1
    assert len(preview["findings_categorized"]["facts"]) >= 1
    assert len(preview["roi_evidence"]) >= 1

    # Check evidence register attributes
    ev_item = preview["evidence_register"][0]
    assert ev_item["original_filename"] == "claim_bumper.jpg"
    assert len(ev_item["sha256_hash"]) == 64
    assert ev_item["status"] in ["VERIFIED", "COMPROMISED"]

    # Check ROI attributes
    roi_item = preview["roi_evidence"][0]
    assert roi_item["roi_label"] == "Bumper Crack Anomaly"
    assert roi_item["width"] == 20
    assert roi_item["height"] == 20


def test_dossier_json_export_and_versioning(client):
    """Verify JSON dossier export, cryptographic hash calculation, and version freezing."""
    case_id, evidence_id, roi_id = _create_sample_case_and_evidence(client)

    res_create = client.post(
        f"/api/v1/cases/{case_id}/dossiers",
        json={"title": "JSON Export Versioning Test"},
    )
    dossier_id = res_create.json()["id"]

    # Export JSON v1
    res_exp1 = client.post(f"/api/v1/dossiers/{dossier_id}/export/json")
    assert res_exp1.status_code == 201
    exp1 = res_exp1.json()

    assert exp1["export_format"] == "JSON"
    assert exp1["version"] == 1
    assert len(exp1["sha256_hash"]) == 64
    assert exp1["filename"].endswith(".json")

    # Export JSON v2 (should increment version and preserve history)
    res_exp2 = client.post(f"/api/v1/dossiers/{dossier_id}/export/json")
    assert res_exp2.status_code == 201
    exp2 = res_exp2.json()

    assert exp2["version"] == 2
    assert exp2["filename"] != exp1["filename"]

    # Verify export history ledger
    res_exports = client.get(f"/api/v1/dossiers/{dossier_id}/exports")
    assert res_exports.status_code == 200
    export_list = res_exports.json()
    assert len(export_list) == 2

    # Download exported JSON
    res_dl = client.get(f"/api/v1/dossiers/{dossier_id}/exports/{exp1['id']}/file")
    assert res_dl.status_code == 200
    assert res_dl.headers["content-type"].startswith("application/json")
    assert res_dl.headers["x-report-sha256"] == exp1["sha256_hash"]


def test_dossier_pdf_export_and_integrity(client):
    """Verify ReportLab multi-page PDF generation, binary header, and download."""
    case_id, evidence_id, roi_id = _create_sample_case_and_evidence(client)

    res_create = client.post(
        f"/api/v1/cases/{case_id}/dossiers",
        json={
            "title": "Multi-Page PDF Forensic Report Test",
            "author": "Dr. Aris Thorne",
            "executive_summary": "Extensive algorithmic evaluation of localized rate-distortion and compression anomalies.",
            "examiner_conclusions": "Evidence supports initial suspicion of localized panel modification.",
        },
    )
    dossier_id = res_create.json()["id"]

    # Generate PDF export
    res_exp = client.post(f"/api/v1/dossiers/{dossier_id}/export/pdf")
    assert res_exp.status_code == 201
    exp = res_exp.json()

    assert exp["export_format"] == "PDF"
    assert exp["version"] == 1
    assert len(exp["sha256_hash"]) == 64
    assert exp["filename"].endswith(".pdf")
    assert exp["file_size"] > 2000

    # Download exported PDF
    res_dl = client.get(f"/api/v1/dossiers/{dossier_id}/exports/{exp['id']}/file")
    assert res_dl.status_code == 200
    assert res_dl.headers["content-type"] == "application/pdf"
    assert res_dl.headers["x-report-sha256"] == exp["sha256_hash"]

    # Verify actual PDF magic bytes
    pdf_content = res_dl.content
    assert pdf_content.startswith(b"%PDF-")
    assert b"%%EOF" in pdf_content
