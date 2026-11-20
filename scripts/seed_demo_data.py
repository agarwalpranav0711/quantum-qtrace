"""
Q-TRACE Demonstration Data Seeder (Synthetic Evidence Only).

Seeds a self-contained, realistic motor insurance forensic investigation case
using strictly synthetic, procedurally-generated imagery.
Demonstrates:
  - Case intake & metadata
  - Evidence ingestion with SHA-256 baselines
  - Classical forensic analysis execution
  - ROI creation and derivative crop generation
  - Homography image comparison and difference heatmap
  - Quantum-assisted 16-qubit patch comparison simulation
  - Formal dossier compilation with structured findings
"""

import io
import json
import uuid
import hashlib
import sys
from pathlib import Path

# Add project root to sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw
import numpy as np

from backend.app.core.config import get_settings
from backend.app.database.session import SessionLocal
from backend.app.models.case import Case
from backend.app.models.note import ExaminerNote
from backend.app.services.case_service import CaseService
from backend.app.services.canvas_service import CanvasService
from backend.app.services.dossier_service import dossier_service
from backend.app.forensics.pipeline import ForensicPipeline
from backend.app.forensics.schemas import AnalysisExecutionRequest
from backend.app.schemas.roi import ROICreate, ImageComparisonRequest
from backend.app.schemas.dossier import DossierCreate
from backend.app.schemas.quantum import QuantumComparisonRequest
from backend.app.integrations.quantum_adapter import QuantumAdapter

settings = get_settings()


def generate_synthetic_demo_image(is_tampered=False) -> bytes:
    """Generate a clean synthetic bumper photograph with distinct structural lines."""
    width, height = 256, 192
    img = Image.new("RGB", (width, height), color=(175, 185, 195))
    draw = ImageDraw.Draw(img)

    # Vehicle body lines and panel contours
    draw.rectangle([20, 20, width - 20, height - 20], outline=(60, 70, 85), width=3)
    draw.line([30, 96, width - 30, 96], fill=(50, 55, 65), width=4)
    draw.ellipse([50, 40, 110, 100], outline=(100, 110, 125), width=2)
    draw.ellipse([width - 110, 40, width - 50, 100], outline=(100, 110, 125), width=2)

    if is_tampered:
        # Simulate an inserted damage dent and brush smoothing
        draw.polygon([(110, 80), (145, 65), (150, 115), (105, 110)], fill=(80, 85, 95), outline=(220, 40, 40))
        draw.line([110, 80, 150, 115], fill=(20, 20, 20), width=3)
        draw.line([145, 65, 105, 110], fill=(25, 25, 25), width=2)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def seed_demo_investigation():
    """Seed comprehensive synthetic demonstration case."""
    print("=" * 60)
    print("  Q-TRACE Demonstration Data Generator (Synthetic Evidence)")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Check if demo case already exists
        existing_case = db.query(Case).filter(Case.case_number == "QC-DEMO-CLAIM-2026").first()
        if existing_case:
            print("  Notice: Demo case 'QC-DEMO-CLAIM-2026' already exists.")
            print("  To reset, run: python scripts/reset_demo_data.py")
            return existing_case.id

        # 2. Create Case
        print("[1/6] Creating Synthetic Forensic Case...")
        case = Case(
            case_number="QC-DEMO-CLAIM-2026",
            title="[DEMO] Front Bumper Collision & Digital Splicing Audit",
            description="Synthetic demonstration case: Motor claim photographic audit verifying localized panel tampering and digital brush inpainting.",
            status="ACTIVE",
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        print(f"  Created Case: {case.case_number} (ID: {case.id})")

        # Add Examiner Notes
        db.add(ExaminerNote(
            case_id=case.id,
            author="Dr. Harrison Thorne, Lead Forensic Investigator",
            content="Initial visual inspection: Claim photograph shows localized gradient irregularities on center bumper panel.",
        ))
        db.commit()

        # 3. Ingest Synthetic Evidence
        print("\n[2/6] Ingesting Synthetic Evidence Images (WORM Storage)...")
        case_svc = CaseService(db)
        suspect_bytes = generate_synthetic_demo_image(is_tampered=True)
        ref_bytes = generate_synthetic_demo_image(is_tampered=False)

        ev_suspect = case_svc.ingest_evidence(
            case_id=case.id,
            original_filename="demo_claim_suspect_bumper.png",
            file_bytes=suspect_bytes,
        )
        print(f"  Ingested Suspect Image: {ev_suspect.original_filename} (SHA-256: {ev_suspect.sha256_hash[:16]}...)")

        ev_ref = case_svc.ingest_evidence(
            case_id=case.id,
            original_filename="demo_baseline_pre_accident.png",
            file_bytes=ref_bytes,
        )
        print(f"  Ingested Reference Image: {ev_ref.original_filename} (SHA-256: {ev_ref.sha256_hash[:16]}...)")

        # 4. Run Classical Forensic Screening
        print("\n[3/6] Running Classical Forensics Pipeline...")
        pipeline = ForensicPipeline(db)
        analysis_summary = pipeline.run_analysis(
            evidence_id=ev_suspect.id,
            request=AnalysisExecutionRequest(techniques=["ela", "noise", "statistics", "perceptual_hash"]),
        )
        print(f"  Completed Analysis: {analysis_summary.overall_status} ({len(analysis_summary.technique_results)} techniques, {len(analysis_summary.artifacts)} artifacts)")

        # 5. Create ROI & Sub-Region Crop
        print("\n[4/6] Creating Region of Interest (ROI) & Generating Lossless Crop...")
        canvas_service = CanvasService(db)
        roi = canvas_service.create_roi(
            evidence_id=ev_suspect.id,
            payload=ROICreate(
                roi_label="Suspect Dent Fracture Inconsistency",
                roi_type="EXAMINER_CREATED",
                x=105,
                y=65,
                width=45,
                height=50,
                color="#EF4444",
                observation="Abrupt noise residual drop and localized ELA variance spike on impact seam.",
                hypothesis="Simulated fracture lines digitally superimposed over pre-existing panel structure.",
                confidence=0.91,
            ),
        )
        crop_resp = canvas_service.generate_roi_crop(roi.id)
        print(f"  Created ROI: {roi.roi_label} [Box: 105,65,45x50] -> Crop: {crop_resp.stored_filename}")

        # 6. Run SIFT Homography Comparison
        print("\n[5/6] Executing Multi-Image Comparison & Alignment...")
        cmp_resp = canvas_service.compare_images(ImageComparisonRequest(
            primary_evidence_id=ev_suspect.id,
            comparison_evidence_id=ev_ref.id,
            align_images=True,
            difference_threshold=15,
        ))
        print(f"  Comparison Completed: SSIM={cmp_resp.ssim_score}, MAE={cmp_resp.mean_absolute_error}, Diff Pixels={cmp_resp.difference_pixel_count}")
        print(f"  Difference Heatmap: {cmp_resp.artifact_filename}")

        # 7. Create Investigation Dossier
        print("\n[6/6] Compiling Forensic Investigation Dossier...")
        dossier = dossier_service.create_dossier(
            db=db,
            case_id=case.id,
            payload=DossierCreate(
                title="Synthetic Demonstration Forensic Dossier: Bumper Tampering Audit",
                author="Dr. Harrison Thorne, Lead Forensic Investigator",
                confidentiality_level="DEMO - SYNTHETIC FORENSIC EVIDENCE ONLY",
                investigation_scope="Controlled evaluation of synthetic motor vehicle claim photographs to demonstrate multi-scale classical forensics and quantum patch comparison.",
                executive_summary="Algorithmic screening identified high-confidence compression and noise residual anomalies concentrated in ROI #1. Digital inpainting of damage fracture edges is indicated.",
                examiner_conclusions="Technical findings support hypothesis of synthetic damage insertion. Physical claim surveyor corroboration recommended.",
                recommendations="Request memory card bitstream or raw image acquisition directly from claimant device.",
                selected_evidence_ids=[ev_suspect.id, ev_ref.id],
                selected_roi_ids=[roi.id],
                include_quantum_experiments=True,
            ),
        )
        print(f"  Created Dossier: {dossier.dossier_number} (Title: {dossier.title})")

        print("\n" + "=" * 60)
        print("  DEMO DATA SUCCESSFULLY SEEDED!")
        print(f"  Case Number:  {case.case_number}")
        print(f"  Dossier ID:   {dossier.id}")
        print("  Open UI at:   http://localhost:5173")
        print("=" * 60)
        return case.id
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_investigation()
