"""
Q-TRACE Part 8: Comprehensive End-to-End Forensic Investigation Workflow Test Suite.

Exercises the entire Q-TRACE platform as a real digital forensics investigator would:
  Step 1: Case Intake & Investigation Workspace Creation
  Step 2: Evidence Ingestion & Cryptographic Baselines
  Step 3: Bitstream Integrity Verification & Anti-Tamper Detection
  Step 4: Classical Forensic Screening (ELA, Noise, CMFD, Histogram, pHash)
  Step 5: Interactive Canvas ROI Selection, Coordinates & Lossless Derivative Crops
  Step 6: SIFT Homography Multi-Image Comparison & Alignment Fallbacks
  Step 7: Quantum-Assisted Verification (4x4 Patch XOR Comparison vs Classical Ground Truth)
  Step 8: Forensic Dossier Assembly & 4-Tier Findings Structuring
  Step 9: Cryptographic PDF & JSON Export with Independent SHA-256 Verification
  Step 10: End-to-End Evidentiary Traceability Audit
"""

import io
import json
import uuid
import hashlib
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import get_settings
from backend.app.database.session import Base, engine, get_db
from backend.app.models.evidence import Evidence
from backend.app.models.case import Case

settings = get_settings()


@pytest.fixture(scope="module")
def client():
    """Module-level TestClient ensuring fresh database schema."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def _generate_synthetic_evidence_image(width=128, height=96, add_tampering=False) -> bytes:
    """Generate deterministic synthetic vehicle panel image for controlled testing."""
    img = Image.new("RGB", (width, height), color=(180, 190, 205))
    draw = ImageDraw.Draw(img)

    # Draw simulated vehicle panel lines and texture
    draw.rectangle([10, 10, width - 10, height - 10], outline=(70, 80, 95), width=2)
    draw.line([20, 48, width - 20, 48], fill=(50, 60, 75), width=3)

    if add_tampering:
        # Simulate localized digital brush/splice anomaly in center
        draw.rectangle([45, 35, 75, 65], fill=(240, 240, 245), outline=(220, 30, 30))
        # Add high-contrast unnatural edge
        draw.line([45, 35, 75, 65], fill=(20, 20, 20), width=2)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_full_investigation_lifecycle_e2e(client):
    """Execute complete 10-step forensic investigation lifecycle end-to-end."""

    # =========================================================================
    # STEP 1: Case Intake & Investigation Workspace Creation
    # =========================================================================
    case_num = f"QC-E2E-{uuid.uuid4().hex[:8].upper()}"
    res_case = client.post(
        "/api/v1/cases",
        json={
            "case_number": case_num,
            "title": "Comprehensive E2E Motor Claim Splicing Audit",
            "description": "Controlled verification of suspect panel fracture photographs.",
        },
    )
    assert res_case.status_code in [200, 201]
    case = res_case.json()
    case_id = case["id"]
    assert case["case_number"] == case_num

    # Add lead investigator note
    res_note = client.post(
        f"/api/v1/cases/{case_id}/notes",
        json={
            "author": "Dr. Elena Vance, Senior Forensic Analyst",
            "content": "Intake initiated: examining digital claim photograph for panel cloning and compression discontinuities.",
        },
    )
    assert res_note.status_code in [200, 201]

    # Verify case retrieval
    res_get_case = client.get(f"/api/v1/cases/{case_id}")
    assert res_get_case.status_code == 200
    assert res_get_case.json()["case_number"] == case_num

    # =========================================================================
    # STEP 2: Evidence Ingestion & Cryptographic Baselines
    # =========================================================================
    raw_img_bytes = _generate_synthetic_evidence_image(128, 96, add_tampering=True)
    expected_sha256 = hashlib.sha256(raw_img_bytes).hexdigest()

    upload_file = ("suspect_vehicle_panel.png", io.BytesIO(raw_img_bytes), "image/png")
    res_upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": upload_file},
        data={"case_id": case_id},
    )
    assert res_upload.status_code in [200, 201]
    evidence = res_upload.json()
    evidence_id = evidence["id"]

    assert evidence["original_filename"] == "suspect_vehicle_panel.png"
    assert evidence["sha256_hash"] == expected_sha256
    assert evidence["file_size"] == len(raw_img_bytes)
    assert evidence["width"] == 128
    assert evidence["height"] == 96

    # =========================================================================
    # STEP 3: Bitstream Integrity Verification & Anti-Tamper Detection
    # =========================================================================
    # 3a. Baseline integrity check
    res_verify = client.post(f"/api/v1/evidence/{evidence_id}/verify")
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert verify_data["is_intact"] is True
    assert verify_data["current_sha256"] == expected_sha256
    assert verify_data["stored_sha256"] == expected_sha256

    # =========================================================================
    # STEP 4: Classical Forensic Screening
    # =========================================================================
    # Run multi-technique forensic pipeline (ELA, NOISE, STATISTICS, PERCEPTUAL_HASH)
    res_analyze = client.post(
        f"/api/v1/evidence/{evidence_id}/analyze",
        json={"techniques": ["ela", "noise", "statistics", "perceptual_hash"]},
    )
    assert res_analyze.status_code in [200, 201]
    analysis = res_analyze.json()
    assert analysis["overall_status"] in ["COMPLETED", "POTENTIAL_INDICATOR_DETECTED", "SUCCESS", "ANALYSIS_COMPLETE"]
    assert len(analysis["technique_results"]) >= 3
    assert len(analysis["artifacts"]) >= 1

    # Inspect analysis history list
    res_analyses_list = client.get(f"/api/v1/evidence/{evidence_id}/analyses")
    assert res_analyses_list.status_code == 200
    all_analyses = res_analyses_list.json()
    assert len(all_analyses) >= 1

    # =========================================================================
    # STEP 5: Interactive Canvas ROI Selection, Coordinates & Lossless Crops
    # =========================================================================
    # Anomaly region at (45, 35) with size 30x30
    res_roi = client.post(
        f"/api/v1/evidence/{evidence_id}/rois",
        json={
            "roi_label": "Suspect Digital Splice Patch",
            "roi_type": "EXAMINER_CREATED",
            "x": 45,
            "y": 35,
            "width": 30,
            "height": 30,
            "color": "#EF4444",
            "observation": "High-contrast edge boundary and noise residual inconsistency with surrounding panel.",
            "hypothesis": "Digital inpainting or spliced patch covering previous damage.",
            "confidence": 0.92,
        },
    )
    assert res_roi.status_code in [200, 201]
    roi = res_roi.json()
    roi_id = roi["id"]
    assert roi["x"] == 45
    assert roi["width"] == 30

    # Generate lossless sub-region derivative crop
    res_crop = client.post(f"/api/v1/rois/{roi_id}/crop")
    assert res_crop.status_code in [200, 201]
    crop_data = res_crop.json()
    assert "artifact_id" in crop_data
    assert crop_data["crop_width"] == 30
    assert crop_data["crop_height"] == 30

    # Stream the derivative artifact and verify valid PNG bytes
    crop_artifact_id = crop_data["artifact_id"]
    res_stream_crop = client.get(f"/api/v1/derivatives/{crop_artifact_id}/file")
    assert res_stream_crop.status_code == 200
    assert res_stream_crop.headers["content-type"] == "image/png"
    assert res_stream_crop.content.startswith(b"\x89PNG\r\n\x1a\n")

    # =========================================================================
    # STEP 6: SIFT Homography Multi-Image Comparison
    # =========================================================================
    # Ingest reference baseline image (without tampering)
    ref_bytes = _generate_synthetic_evidence_image(128, 96, add_tampering=False)
    res_ref_upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("reference_panel_baseline.png", io.BytesIO(ref_bytes), "image/png")},
        data={"case_id": case_id},
    )
    assert res_ref_upload.status_code in [200, 201]
    ref_evidence_id = res_ref_upload.json()["id"]

    # Execute image-to-image comparison
    res_cmp = client.post(
        "/api/v1/evidence/compare",
        json={
            "primary_evidence_id": evidence_id,
            "comparison_evidence_id": ref_evidence_id,
            "align_images": True,
            "difference_threshold": 15,
        },
    )
    assert res_cmp.status_code in [200, 201]
    cmp_result = res_cmp.json()
    assert "mean_absolute_error" in cmp_result
    assert "ssim_score" in cmp_result
    assert "artifact_id" in cmp_result

    # Stream generated difference heatmap artifact
    diff_art_id = cmp_result["artifact_id"]
    res_stream_diff = client.get(f"/api/v1/derivatives/{diff_art_id}/file")
    assert res_stream_diff.status_code == 200
    assert res_stream_diff.headers["content-type"] == "image/png"

    # =========================================================================
    # STEP 7: Quantum-Assisted Verification (4x4 Patch Simulation)
    # =========================================================================
    # 4x4 4-bit grayscale patch pairs (values 0..15)
    patch_a = [
        [5, 5, 5, 5],
        [5, 15, 15, 5],
        [5, 15, 15, 5],
        [5, 5, 5, 5],
    ]
    patch_b = [
        [5, 5, 5, 5],
        [5, 5, 5, 5],
        [5, 5, 5, 5],
        [5, 5, 5, 5],
    ]

    res_quantum = client.post(
        "/api/v1/quantum/compare",
        json={
            "patch_a": patch_a,
            "patch_b": patch_b,
            "architecture": "16q",
            "shots": 512,
        },
    )
    assert res_quantum.status_code == 200
    q_result = res_quantum.json()
    assert q_result["architecture"] == "16q"
    assert q_result["shots_used"] == 512
    assert q_result["difference_count"] == 4
    assert q_result["identical"] is False
    assert q_result["fidelity"] == 1.0

    # Verify classical XOR ground truth parity
    assert q_result["reconstructed_diff_map"] == q_result["classical_diff_map"]

    # =========================================================================
    # STEP 8: Forensic Dossier Assembly & 4-Tier Findings Structuring
    # =========================================================================
    res_dossier = client.post(
        f"/api/v1/cases/{case_id}/dossiers",
        json={
            "title": "Final Forensic Dossier: Suspect Panel Tampering Investigation",
            "author": "Dr. Elena Vance, Senior Forensic Analyst",
            "confidentiality_level": "STRICTLY CONFIDENTIAL - DIGITAL EVIDENCE",
            "investigation_scope": "Comprehensive evaluation of photographic evidence for localized brush tampering and edge discontinuities.",
            "executive_summary": "Algorithmic screening and high-magnification canvas analysis confirmed localized splicing across vehicle panel.",
            "examiner_conclusions": "Technical evidence substantiates artificial modification in ROI #1. Recommend physical vehicle inspection.",
            "recommendations": "Request memory card bitstream or original raw camera source.",
            "selected_evidence_ids": [evidence_id, ref_evidence_id],
            "selected_roi_ids": [roi_id],
            "include_quantum_experiments": True,
        },
    )
    assert res_dossier.status_code == 201
    dossier = res_dossier.json()
    dossier_id = dossier["id"]
    assert len(dossier["sections"]) == 13

    # Verify compiled structured preview
    res_preview = client.get(f"/api/v1/dossiers/{dossier_id}/preview")
    assert res_preview.status_code == 200
    preview = res_preview.json()
    assert len(preview["evidence_register"]) == 2
    assert len(preview["roi_evidence"]) == 1
    assert len(preview["findings_categorized"]["facts"]) >= 2

    # =========================================================================
    # STEP 9: Cryptographic PDF & JSON Export with Independent SHA-256 Verification
    # =========================================================================
    # 9a. Export JSON Dossier
    res_json_exp = client.post(f"/api/v1/dossiers/{dossier_id}/export/json")
    assert res_json_exp.status_code == 201
    json_meta = res_json_exp.json()
    assert json_meta["export_format"] == "JSON"
    assert json_meta["version"] == 1

    # Download exported JSON and compute SHA-256 independently
    res_dl_json = client.get(f"/api/v1/dossiers/{dossier_id}/exports/{json_meta['id']}/file")
    assert res_dl_json.status_code == 200
    downloaded_json_bytes = res_dl_json.content
    calc_json_sha256 = hashlib.sha256(downloaded_json_bytes).hexdigest()

    assert calc_json_sha256 == json_meta["sha256_hash"], "JSON SHA-256 mismatch with DB record!"
    assert res_dl_json.headers["x-report-sha256"] == calc_json_sha256, "JSON SHA-256 header mismatch!"

    # 9b. Export PDF Dossier
    res_pdf_exp = client.post(f"/api/v1/dossiers/{dossier_id}/export/pdf")
    assert res_pdf_exp.status_code == 201
    pdf_meta = res_pdf_exp.json()
    assert pdf_meta["export_format"] == "PDF"
    assert pdf_meta["version"] >= 1

    # Download exported PDF and compute SHA-256 independently
    res_dl_pdf = client.get(f"/api/v1/dossiers/{dossier_id}/exports/{pdf_meta['id']}/file")
    assert res_dl_pdf.status_code == 200
    downloaded_pdf_bytes = res_dl_pdf.content
    calc_pdf_sha256 = hashlib.sha256(downloaded_pdf_bytes).hexdigest()

    assert calc_pdf_sha256 == pdf_meta["sha256_hash"], "PDF SHA-256 mismatch with DB record!"
    assert res_dl_pdf.headers["x-report-sha256"] == calc_pdf_sha256, "PDF SHA-256 header mismatch!"
    assert downloaded_pdf_bytes.startswith(b"%PDF-"), "Invalid PDF binary header!"
    assert b"%%EOF" in downloaded_pdf_bytes, "Invalid PDF binary trailer!"

    # Verify that export hash is NOT the placeholder text sha256(b"1")
    placeholder_hash = hashlib.sha256(b"1").hexdigest()
    assert calc_pdf_sha256 != placeholder_hash, "PDF hash matches single-byte placeholder!"

    # =========================================================================
    # STEP 10: End-to-End Evidentiary Traceability Audit
    # =========================================================================
    # Trace from exported JSON report back to the original source evidence SHA-256
    exported_dossier_doc = json.loads(downloaded_json_bytes.decode("utf-8"))

    # 1. Trace case number
    assert exported_dossier_doc["case_number"] == case_num

    # 2. Trace evidence register items back to original ingestion
    found_evidence_in_export = False
    for ev_item in exported_dossier_doc["evidence_register"]:
        if ev_item["id"] == evidence_id:
            found_evidence_in_export = True
            assert ev_item["sha256_hash"] == expected_sha256
            assert ev_item["original_filename"] == "suspect_vehicle_panel.png"
    assert found_evidence_in_export is True, "Original evidence was not traceable in export!"

    # 3. Trace ROI annotation and crop back to source
    found_roi_in_export = False
    for roi_item in exported_dossier_doc["roi_evidence"]:
        if roi_item["id"] == roi_id:
            found_roi_in_export = True
            assert roi_item["evidence_id"] == evidence_id
            assert roi_item["roi_label"] == "Suspect Digital Splice Patch"
            assert roi_item["confidence"] == 0.92
    assert found_roi_in_export is True, "ROI was not traceable in export!"

    # 4. Verify version history preserves prior exports
    res_hist = client.get(f"/api/v1/dossiers/{dossier_id}/exports")
    assert res_hist.status_code == 200
    export_history = res_hist.json()
    assert len(export_history) >= 2



def test_evidence_tamper_detection_in_isolated_env(client):
    """Test that modifying physical evidence bytes triggers tamper detection in verify endpoint."""
    case_num = f"QC-TAMPER-{uuid.uuid4().hex[:8].upper()}"
    res_case = client.post("/api/v1/cases", json={"case_number": case_num, "title": "Tamper Test Case"})
    case_id = res_case.json()["id"]

    # Generate unique image to avoid WORM collision with prior test runs
    img = Image.new("RGB", (64, 48), color=(120, 140, 160))
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), str(uuid.uuid4()), fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    upload_file = ("clean_evidence.png", io.BytesIO(raw_bytes), "image/png")
    res_upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": upload_file},
        data={"case_id": case_id},
    )
    assert res_upload.status_code in [200, 201]
    ev_data = res_upload.json()
    ev_id = ev_data["id"]
    stored_fn = ev_data["stored_filename"]

    # Verify baseline is intact
    res_v1 = client.post(f"/api/v1/evidence/{ev_id}/verify")
    assert res_v1.json()["is_intact"] is True

    # Simulate bitstream tampering directly on the physical storage file
    from backend.app.storage.service import get_storage_service
    storage = get_storage_service()
    physical_path = storage.retrieve_file("originals", stored_fn)
    import stat
    import os
    orig_file_bytes = physical_path.read_bytes()
    try:
        os.chmod(physical_path, stat.S_IWRITE | stat.S_IREAD)
        with open(physical_path, "ab") as f:
            f.write(b"TAMPER_PAYLOAD")

        # Re-verify and confirm detection
        res_v2 = client.post(f"/api/v1/evidence/{ev_id}/verify")
        assert res_v2.status_code == 200
        v2_data = res_v2.json()
        assert v2_data["is_intact"] is False
        assert v2_data["status"] == "COMPROMISED"
        assert "TAMPER" in v2_data["message"].upper() or "NOT MATCH" in v2_data["message"].upper()
    finally:
        # Restore original bytes and read-only mode so subsequent runs stay consistent
        with open(physical_path, "wb") as f:
            f.write(orig_file_bytes)
        os.chmod(physical_path, stat.S_IREAD)


def test_homography_alignment_fallback_on_featureless_images(client):
    """Verify SIFT homography alignment gracefully falls back to identity when no features match."""
    case_num = f"QC-ALIGN-{uuid.uuid4().hex[:8].upper()}"
    res_case = client.post("/api/v1/cases", json={"case_number": case_num, "title": "Featureless Align Case"})
    case_id = res_case.json()["id"]

    # Solid white image
    img_white = Image.new("RGB", (64, 64), color=(255, 255, 255))
    buf_w = io.BytesIO()
    img_white.save(buf_w, format="PNG")

    # Solid black image
    img_black = Image.new("RGB", (64, 64), color=(0, 0, 0))
    buf_b = io.BytesIO()
    img_black.save(buf_b, format="PNG")

    res_w = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("white.png", io.BytesIO(buf_w.getvalue()), "image/png")},
        data={"case_id": case_id},
    )
    id_w = res_w.json()["id"]

    res_b = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("black.png", io.BytesIO(buf_b.getvalue()), "image/png")},
        data={"case_id": case_id},
    )
    id_b = res_b.json()["id"]

    # Compare with align_images=True; should gracefully handle fallback
    res_cmp = client.post(
        "/api/v1/evidence/compare",
        json={
            "primary_evidence_id": id_w,
            "comparison_evidence_id": id_b,
            "align_images": True,
        },
    )
    assert res_cmp.status_code == 200
    cmp_data = res_cmp.json()
    assert cmp_data["alignment_status"] in ["FALLBACK_IDENTITY", "IDENTICAL_GRID", "FAILED", "SKIPPED"]
    assert cmp_data["mean_absolute_error"] == 255.0
    assert cmp_data["difference_percentage"] == 100.0


def test_quantum_comparison_edge_cases(client):
    """Verify quantum simulation edge cases: identical patches, max intensity, zero-valued."""
    # 1. Identical zero patches
    patch_zeros = [[0]*4 for _ in range(4)]
    res_zero = client.post(
        "/api/v1/quantum/compare",
        json={"patch_a": patch_zeros, "patch_b": patch_zeros, "architecture": "16q", "shots": 256},
    )
    assert res_zero.status_code == 200
    zero_data = res_zero.json()
    assert zero_data["identical"] is True
    assert zero_data["difference_count"] == 0

    # 2. Maximum intensity difference (0 vs 15)
    patch_max = [[15]*4 for _ in range(4)]
    res_max = client.post(
        "/api/v1/quantum/compare",
        json={"patch_a": patch_zeros, "patch_b": patch_max, "architecture": "12q", "shots": 256},
    )
    assert res_max.status_code == 200
    max_data = res_max.json()
    assert max_data["identical"] is False
    assert max_data["difference_count"] == 16
    assert max_data["architecture"] == "12q"
