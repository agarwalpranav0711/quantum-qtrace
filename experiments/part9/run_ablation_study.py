"""
Q-TRACE Part 9: Multi-Technique Forensic Ablation Study & Consensus Evaluation
Evaluates single techniques (ELA, Noise, CMFD), pairwise combinations,
and full multi-technique consensus fusion across varied attack modalities
to measure precision, recall, false positive reduction, and IoU localization.
"""

import json
import csv
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.storage.service import StorageService
from backend.app.forensics.ela_analyzer import ErrorLevelAnalyzer
from backend.app.forensics.noise_analyzer import NoiseAnalyzer
from backend.app.forensics.copy_move_analyzer import CopyMoveAnalyzer
from backend.app.forensics.consensus_fusion import fuse_candidate_regions
from backend.app.forensics.schemas import RegionOfInterest
from experiments.part9.run_classical_benchmark import (
    create_pristine_vehicle_panel,
    create_spliced_case,
    create_copymove_case,
    create_noise_inconsistent_case,
    compute_binary_metrics,
)


def evaluate_technique_subset(
    subset_name: str,
    res_dict: Dict[str, Any],
    technique_keys: List[str],
    gt_mask: np.ndarray,
    min_consensus: int = 1,
) -> Dict[str, Any]:
    """Combines ROIs from specified techniques and computes validation metrics."""
    sub_dict = {k: res_dict[k] for k in technique_keys}
    if len(technique_keys) > 1:
        fused = fuse_candidate_regions(sub_dict, iou_threshold=0.20)
        if min_consensus > 1:
            fused = [r for r in fused if len(r.contributing_techniques) >= min_consensus]
    else:
        fused = res_dict[technique_keys[0]].candidate_regions

    metrics = compute_binary_metrics(gt_mask, fused)
    return {
        "configuration": subset_name,
        "techniques": "+".join(technique_keys),
        "min_consensus": min_consensus,
        "roi_count": len(fused),
        **metrics,
    }


def main():
    print("=" * 70)
    print("Q-TRACE Part 9: Forensic Fusion Ablation Study")
    print("=" * 70)

    out_dir = PROJECT_ROOT / "results" / "part9" / "ablation"
    out_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(tempfile.mkdtemp(prefix="qtrace_ablation_bench_"))
    storage = StorageService(root_path=temp_dir)

    ela_analyzer = ErrorLevelAnalyzer()
    noise_analyzer = NoiseAnalyzer()
    cmfd_analyzer = CopyMoveAnalyzer()

    # Create composite multi-attack dataset
    base_panel = create_pristine_vehicle_panel(320, 320, seed=42)
    spliced_bytes, spliced_gt = create_spliced_case(base_panel)
    cm_bytes, cm_gt = create_copymove_case(base_panel)
    noise_bytes, noise_gt = create_noise_inconsistent_case(base_panel)

    _, clean_enc = cv2.imencode(".jpg", base_panel, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    clean_bytes = clean_enc.tobytes()
    clean_gt = np.zeros((320, 320), dtype=np.uint8)

    test_samples = [
        ("Splicing", spliced_bytes, spliced_gt, "jpg"),
        ("Copy-Move", cm_bytes, cm_gt, "png"),
        ("Noise-Inconsistency", noise_bytes, noise_gt, "png"),
        ("Clean-Authentic", clean_bytes, clean_gt, "jpg"),
    ]

    configurations = [
        ("Single-ELA", ["ela"], 1),
        ("Single-Noise", ["noise"], 1),
        ("Single-CMFD", ["cmfd"], 1),
        ("Pairwise-ELA+Noise-Union", ["ela", "noise"], 1),
        ("Pairwise-ELA+Noise-Consensus", ["ela", "noise"], 2),
        ("Pairwise-ELA+CMFD-Union", ["ela", "cmfd"], 1),
        ("Pairwise-Noise+CMFD-Union", ["noise", "cmfd"], 1),
        ("Full-Ensemble-Union", ["ela", "noise", "cmfd"], 1),
        ("Full-Ensemble-Consensus-2+", ["ela", "noise", "cmfd"], 2),
    ]

    all_rows = []

    print("\n[1/2] Executing Multi-Modal Ablation Runs...")
    for attack_name, b, gt, ext in test_samples:
        print(f"  Analyzing sample: {attack_name}...")
        ela_res = ela_analyzer.analyze(Path(f"sample.{ext}"), b, {"quality": 95, "scale": 15}, storage, f"ela_{attack_name}")
        noise_res = noise_analyzer.analyze(Path(f"sample.{ext}"), b, {}, storage, f"noise_{attack_name}")
        cmfd_res = cmfd_analyzer.analyze(Path(f"sample.{ext}"), b, {}, storage, f"cmfd_{attack_name}")

        res_dict = {
            "ela": ela_res,
            "noise": noise_res,
            "cmfd": cmfd_res,
        }

        for config_name, tech_list, min_c in configurations:
            row = evaluate_technique_subset(
                subset_name=config_name,
                res_dict=res_dict,
                technique_keys=tech_list,
                gt_mask=gt,
                min_consensus=min_c,
            )
            row["attack_type"] = attack_name
            all_rows.append(row)

    # Save outputs
    matrix_csv = out_dir / "ablation_study_matrix.csv"
    with open(matrix_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["attack_type", "configuration", "techniques", "min_consensus", "roi_count",
                      "precision", "recall", "f1", "specificity", "iou", "tp_pixels", "fp_pixels", "fn_pixels", "tn_pixels"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    # Compute aggregate summary across configurations
    summary_by_config = {}
    for c_name, _, _ in configurations:
        c_rows = [r for r in all_rows if r["configuration"] == c_name]
        # Clean false positive rate
        clean_fp_pixels = sum(r["fp_pixels"] for r in c_rows if r["attack_type"] == "Clean-Authentic")
        # Forgery recall
        forgery_recalls = [r["recall"] for r in c_rows if r["attack_type"] != "Clean-Authentic"]
        forgery_ious = [r["iou"] for r in c_rows if r["attack_type"] != "Clean-Authentic"]
        forgery_f1s = [r["f1"] for r in c_rows if r["attack_type"] != "Clean-Authentic"]

        summary_by_config[c_name] = {
            "mean_forgery_recall": round(float(np.mean(forgery_recalls)), 4),
            "mean_forgery_iou": round(float(np.mean(forgery_ious)), 4),
            "mean_forgery_f1": round(float(np.mean(forgery_f1s)), 4),
            "clean_control_fp_pixels": int(clean_fp_pixels),
        }

    summary_json = out_dir / "ablation_study_summary.json"
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "configurations_evaluated": len(configurations),
            "summary_by_configuration": summary_by_config,
            "raw_evaluations_count": len(all_rows),
        }, f, indent=2)

    print(f"\n[OK] Ablation results saved to {out_dir}:")
    print(f"  - {matrix_csv.name}")
    print(f"  - {summary_json.name}")
    print("Ablation study complete.")


if __name__ == "__main__":
    main()
