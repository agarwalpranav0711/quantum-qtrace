"""
Q-TRACE Safe Demonstration Data Reset Utility.

SAFETY GUARDRAILS:
  - This script ONLY targets synthetic demo cases matching the pattern 'QC-DEMO-%'.
  - It will NEVER modify, delete, or truncate genuine forensic cases or user evidence.
  - Exits safely with zero changes if no demo records are found.
"""

import sys
from pathlib import Path

# Add project root to sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import get_settings
from backend.app.database.session import SessionLocal
from backend.app.models.case import Case
from backend.app.models.evidence import Evidence
from backend.app.models.artifact import Artifact
from backend.app.models.analysis import Analysis
from backend.app.models.roi import RegionOfInterestModel
from backend.app.models.note import ExaminerNote
from backend.app.models.dossier import DossierModel, DossierSectionModel, DossierExportModel
from backend.app.storage.service import get_storage_service

settings = get_settings()


def reset_demo_data():
    """Safely find and purge only demo cases and their associated synthetic artifacts."""
    print("=" * 60)
    print("  Q-TRACE Safe Demonstration Data Reset")
    print("  Target Scope: Only cases matching 'QC-DEMO-%'")
    print("=" * 60)

    storage = get_storage_service()

    db = SessionLocal()
    try:
        demo_cases = db.query(Case).filter(Case.case_number.like("QC-DEMO-%")).all()
        if not demo_cases:
            print("  No synthetic demonstration cases found. Zero records touched.")
            return

        print(f"  Found {len(demo_cases)} synthetic demonstration case(s):")
        for c in demo_cases:
            print(f"    - {c.case_number}: '{c.title}' (ID: {c.id})")

        total_evidence_purged = 0
        total_artifacts_purged = 0

        for case in demo_cases:
            # 1. Purge Dossiers and Exports
            dossiers = db.query(DossierModel).filter(DossierModel.case_id == case.id).all()
            for d in dossiers:
                exports = db.query(DossierExportModel).filter(DossierExportModel.dossier_id == d.id).all()
                for exp in exports:
                    # Remove exported file if exists
                    try:
                        p = Path(exp.file_path).resolve()
                        if p.exists() and "storage" in str(p):
                            p.unlink(missing_ok=True)
                    except Exception:
                        pass
                    db.delete(exp)
                db.query(DossierSectionModel).filter(DossierSectionModel.dossier_id == d.id).delete()
                db.delete(d)

            # 2. Purge Evidence, ROIs, and Analyses
            evidence_items = db.query(Evidence).filter(Evidence.case_id == case.id).all()
            for ev in evidence_items:
                total_evidence_purged += 1
                # Purge ROIs
                db.query(RegionOfInterestModel).filter(RegionOfInterestModel.evidence_id == ev.id).delete()

                # Purge Analyses & Artifacts
                analyses = db.query(Analysis).filter(Analysis.evidence_id == ev.id).all()
                for ana in analyses:
                    artifacts = db.query(Artifact).filter(Artifact.analysis_id == ana.id).all()
                    for art in artifacts:
                        total_artifacts_purged += 1
                        try:
                            if art.file_path:
                                ap = Path(art.file_path).resolve()
                                if ap.exists() and "storage" in str(ap):
                                    ap.unlink(missing_ok=True)
                        except Exception:
                            pass
                        db.delete(art)
                    db.delete(ana)

                # Remove original demo evidence file
                try:
                    ev_path = storage.get_category_dir("originals") / ev.stored_filename
                    if ev_path.exists():
                        import os, stat
                        os.chmod(ev_path, stat.S_IWRITE | stat.S_IREAD)
                        ev_path.unlink(missing_ok=True)
                except Exception:
                    pass

                db.delete(ev)

            # 3. Purge Notes and Case
            db.query(ExaminerNote).filter(ExaminerNote.case_id == case.id).delete()
            db.delete(case)

        db.commit()
        print(f"\n  Successfully purged demonstration records:")
        print(f"    - Cases deleted:     {len(demo_cases)}")
        print(f"    - Evidence deleted:  {total_evidence_purged}")
        print(f"    - Artifacts deleted: {total_artifacts_purged}")
        print("  All user cases, real evidence, and databases remain 100% intact.")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    reset_demo_data()
