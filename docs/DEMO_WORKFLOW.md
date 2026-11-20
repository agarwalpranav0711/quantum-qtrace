# Q-TRACE Demonstration Data & Safe Reset Workflow

## 1. Principles of Demonstration Safety

In digital forensic applications, demonstration data must never contaminate genuine forensic cases or user evidence. Q-TRACE enforces three strict safety guardrails:
1. **Procedural Synthetic Data Only**: Demo evidence is generated entirely using procedural vector and raster operations (`PIL.ImageDraw`). No actual vehicles, claimants, or copyright-restricted images are used.
2. **Deterministic Identifier Namespacing**: All demo cases and dossiers are prefixed with `QC-DEMO-`.
3. **Protected Reset Mechanism**: The reset script (`scripts/reset_demo_data.py`) exclusively queries cases matching `QC-DEMO-%`. It is mathematically impossible for the reset script to delete or mutate genuine user cases.

---

## 2. Seeding Synthetic Demonstration Data

To populate the workstation with a complete end-to-end investigation case:

```powershell
python scripts/seed_demo_data.py
```

### Generated Demonstration Case Overview:
- **Case Number:** `QC-DEMO-CLAIM-2026`
- **Case Title:** `[DEMO] Front Bumper Collision & Digital Splicing Audit`
- **Suspect Evidence:** `demo_claim_suspect_bumper.png` (256x192 PNG with simulated impact dent and localized inpainting).
- **Reference Evidence:** `demo_baseline_pre_accident.png` (256x192 PNG baseline vehicle panel).
- **Forensic Analyses Executed:** ELA, Noise Variance, Multi-Channel Statistics, and Perceptual Hashing.
- **ROI Defined:** `Suspect Dent Fracture Inconsistency` (Bounding box `[105, 65, 45x50]`, confidence 0.91) with an automatic lossless derivative crop (`crop_*.png`).
- **Image Comparison:** SIFT homography alignment with MAE, SSIM (0.9578), and a difference heatmap artifact (`diff_*.png`).
- **Dossier Assembled:** `DOS-QC-DEMO-CLAIM-2026-01` featuring structured 4-tier findings and examiner observations.

---

## 3. Purging Demonstration Data Safely

To safely remove all synthetic demonstration data and restore a clean workstation:

```powershell
python scripts/reset_demo_data.py
```

### Safety Log Verification:
```text
============================================================
  Q-TRACE Safe Demonstration Data Reset
  Target Scope: Only cases matching 'QC-DEMO-%'
============================================================
  Found 1 synthetic demonstration case(s):
    - QC-DEMO-CLAIM-2026: '[DEMO] Front Bumper Collision & Digital Splicing Audit' (ID: ...)

  Successfully purged demonstration records:
    - Cases deleted:     1
    - Evidence deleted:  2
    - Artifacts deleted: 2
  All user cases, real evidence, and databases remain 100% intact.
============================================================
```

