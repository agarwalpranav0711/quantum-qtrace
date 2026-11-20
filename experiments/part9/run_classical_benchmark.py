"""
Q-TRACE Part 9: Classical Forensic Validation & Benchmark Suite
Generates controlled synthetic test cases with pixel-level ground truth masks,
evaluates ELA, Noise Inconsistency, Copy-Move (CMFD), and Consensus Fusion,
and computes Precision, Recall, F1, Specificity, IoU, and execution latencies.
"""

import io
import time
import json
import csv
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.storage.service import StorageService
from backend.app.forensics.ela_analyzer import ErrorLevelAnalyzer
from backend.app.forensics.noise_analyzer import NoiseAnalyzer
from backend.app.forensics.copy_move_analyzer import CopyMoveAnalyzer
from backend.app.forensics.consensus_fusion import fuse_candidate_regions
from backend.app.forensics.schemas import RegionOfInterest


def create_pristine_vehicle_panel(width: int = 320, height: int = 320, seed: int = 42) -> np.ndarray:
    """Generate a realistic textured metallic vehicle panel."""
    rng = np.random.default_rng(seed)
    # Gradient metallic base
    y, x = np.mgrid[0:height, 0:width]
    base = 140 + 40 * (np.sin(x / 50.0) * np.cos(y / 60.0))
    img = np.dstack([base, base + 5, base + 15]).astype(np.float32)

    # Add realistic high-frequency metal flake sensor noise
    sensor_noise = rng.normal(0, 3.5, (height, width, 3))
    panel = np.clip(img + sensor_noise, 0, 255).astype(np.uint8)

    # Add vehicle panel body seam line
    cv2.line(panel, (0, int(height * 0.45)), (width, int(height * 0.45)), (50, 50, 55), 2)
    return panel


def create_spliced_case(base_panel: np.ndarray, quality_base: int = 95, quality_patch: int = 40) -> Tuple[bytes, np.ndarray]:
    """Insert a foreign patch with mismatched compression history and return (image_bytes, ground_truth_mask)."""
    h, w, c = base_panel.shape
    gt_mask = np.zeros((h, w), dtype=np.uint8)

    # Encode base to JPEG
    _, base_enc = cv2.imencode(".jpg", base_panel, [int(cv2.IMWRITE_JPEG_QUALITY), quality_base])
    base_decoded = cv2.imdecode(base_enc, cv2.IMREAD_COLOR)

    # Create foreign patch
    patch_w, patch_h = 70, 70
    patch_x, patch_y = 120, 100
    foreign_patch = np.zeros((patch_h, patch_w, 3), dtype=np.uint8)
    foreign_patch[:, :] = (30, 45, 190)  # Reddish rust / foreign paint texture
    # Add harsh high-contrast texture to patch
    rng = np.random.default_rng(101)
    foreign_patch = np.clip(foreign_patch.astype(np.int16) + rng.integers(-40, 40, (patch_h, patch_w, 3)), 0, 255).astype(np.uint8)

    # Encode foreign patch at different compression quality
    _, patch_enc = cv2.imencode(".jpg", foreign_patch, [int(cv2.IMWRITE_JPEG_QUALITY), quality_patch])
    patch_decoded = cv2.imdecode(patch_enc, cv2.IMREAD_COLOR)

    # Splice patch into base
    composite = base_decoded.copy()
    composite[patch_y:patch_y+patch_h, patch_x:patch_x+patch_w] = patch_decoded
    gt_mask[patch_y:patch_y+patch_h, patch_x:patch_x+patch_w] = 1

    # Final save at high quality
    _, final_enc = cv2.imencode(".jpg", composite, [int(cv2.IMWRITE_JPEG_QUALITY), quality_base])
    return final_enc.tobytes(), gt_mask


def create_copymove_case(base_panel: np.ndarray) -> Tuple[bytes, np.ndarray]:
    """Duplicate a textured feature region within the same image."""
    h, w, c = base_panel.shape
    gt_mask = np.zeros((h, w), dtype=np.uint8)
    rng = np.random.default_rng(202)

    composite = base_panel.copy()
    # Create dent / scratch high-entropy feature patch
    patch_size = 45
    src_x, src_y = 40, 50
    dst_x, dst_y = 180, 190

    # Draw dent texture at source
    dent_texture = rng.integers(20, 230, (patch_size, patch_size, 3), dtype=np.uint8)
    composite[src_y:src_y+patch_size, src_x:src_x+patch_size] = dent_texture
    # Copy to destination (forgery)
    composite[dst_y:dst_y+patch_size, dst_x:dst_x+patch_size] = dent_texture

    # Mark both or target as manipulated (in forensic convention, cloned region is target)
    gt_mask[dst_y:dst_y+patch_size, dst_x:dst_x+patch_size] = 1

    # Save as lossless PNG to avoid compression artifacts overriding SIFT descriptors
    _, final_enc = cv2.imencode(".png", composite)
    return final_enc.tobytes(), gt_mask


def create_noise_inconsistent_case(base_panel: np.ndarray) -> Tuple[bytes, np.ndarray]:
    """Inject localized inconsistent noise variance (e.g. smoothed retouching)."""
    h, w, c = base_panel.shape
    gt_mask = np.zeros((h, w), dtype=np.uint8)

    composite = base_panel.copy()
    patch_w, patch_h = 60, 60
    patch_x, patch_y = 130, 130

    # Retouching / airbrushing: heavy Gaussian blur on specific region to destroy natural sensor noise
    sub = composite[patch_y:patch_y+patch_h, patch_x:patch_x+patch_w]
    blurred_sub = cv2.GaussianBlur(sub, (15, 15), 5.0)
    composite[patch_y:patch_y+patch_h, patch_x:patch_x+patch_w] = blurred_sub
    gt_mask[patch_y:patch_y+patch_h, patch_x:patch_x+patch_w] = 1

    _, final_enc = cv2.imencode(".png", composite)
    return final_enc.tobytes(), gt_mask


def compute_binary_metrics(gt_mask: np.ndarray, detected_rois: List[RegionOfInterest]) -> Dict[str, float]:
    """Calculate pixel-level confusion matrix and derived forensic metrics."""
    h, w = gt_mask.shape
    pred_mask = np.zeros((h, w), dtype=np.uint8)

    for roi in detected_rois:
        rx = max(0, min(w - 1, int(roi.x)))
        ry = max(0, min(h - 1, int(roi.y)))
        rw = max(1, min(w - rx, int(roi.width)))
        rh = max(1, min(h - ry, int(roi.height)))
        pred_mask[ry:ry+rh, rx:rx+rw] = 1

    tp = int(np.sum((gt_mask == 1) & (pred_mask == 1)))
    fp = int(np.sum((gt_mask == 0) & (pred_mask == 1)))
    fn = int(np.sum((gt_mask == 1) & (pred_mask == 0)))
    tn = int(np.sum((gt_mask == 0) & (pred_mask == 0)))

    eps = 1e-9
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * (precision * recall) / (precision + recall + eps)
    specificity = tn / (tn + fp + eps)
    iou = tp / (tp + fp + fn + eps)

    return {
        "tp_pixels": tp,
        "fp_pixels": fp,
        "fn_pixels": fn,
        "tn_pixels": tn,
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "specificity": round(float(specificity), 4),
        "iou": round(float(iou), 4),
    }


def main():
    print("=" * 70)
    print("Q-TRACE Part 9: Classical Forensic Scientific Benchmark")
    print("=" * 70)

    out_dir = PROJECT_ROOT / "results" / "part9" / "classical"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Initialize storage and analyzers
    temp_dir = Path(tempfile.mkdtemp(prefix="qtrace_classical_bench_"))
    storage = StorageService(root_path=temp_dir)
    ela_analyzer = ErrorLevelAnalyzer()
    noise_analyzer = NoiseAnalyzer()
    cmfd_analyzer = CopyMoveAnalyzer()

    # Generate benchmark test dataset
    print("\n[1/3] Generating Controlled Synthetic Dataset...")
    base_panel = create_pristine_vehicle_panel(320, 320, seed=42)

    test_scenarios = []

    # Scenario 1: Spliced patch (compression mismatch)
    spliced_bytes, spliced_gt = create_spliced_case(base_panel, quality_base=95, quality_patch=40)
    test_scenarios.append({
        "scenario_id": "SYN-SPLICE-01",
        "attack_type": "Splicing",
        "description": "Foreign patch inserted with compression difference Q95 vs Q40",
        "bytes": spliced_bytes,
        "gt_mask": spliced_gt,
        "extension": "jpg"
    })

    # Scenario 2: Copy-Move duplication
    cm_bytes, cm_gt = create_copymove_case(base_panel)
    test_scenarios.append({
        "scenario_id": "SYN-CMFD-01",
        "attack_type": "Copy-Move",
        "description": "High-texture dent feature duplicated across panel",
        "bytes": cm_bytes,
        "gt_mask": cm_gt,
        "extension": "png"
    })

    # Scenario 3: Noise inconsistency / retouching
    noise_bytes, noise_gt = create_noise_inconsistent_case(base_panel)
    test_scenarios.append({
        "scenario_id": "SYN-NOISE-01",
        "attack_type": "Noise Inconsistency",
        "description": "Localized Gaussian smoothing destroying sensor noise",
        "bytes": noise_bytes,
        "gt_mask": noise_gt,
        "extension": "png"
    })

    # Scenario 4: Pristine authentic panel (False Positive control)
    _, pristine_enc = cv2.imencode(".jpg", base_panel, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    pristine_bytes = pristine_enc.tobytes()
    pristine_gt = np.zeros((320, 320), dtype=np.uint8)
    test_scenarios.append({
        "scenario_id": "SYN-CLEAN-01",
        "attack_type": "Authentic Control",
        "description": "Unmanipulated authentic metallic panel",
        "bytes": pristine_bytes,
        "gt_mask": pristine_gt,
        "extension": "jpg"
    })

    # Run evaluations
    print(f"\n[2/3] Executing Classical Forensic Evaluations on {len(test_scenarios)} scenarios...")
    results_detail = []
    
    for sc in test_scenarios:
        sc_id = sc["scenario_id"]
        img_bytes = sc["bytes"]
        gt_mask = sc["gt_mask"]
        ext = sc["extension"]

        print(f"  Evaluating {sc_id} ({sc['attack_type']})...")

        # 1. ELA
        t0 = time.perf_counter()
        ela_res = ela_analyzer.analyze(Path(f"{sc_id}.{ext}"), img_bytes, {"quality": 95, "scale": 15}, storage, f"ela_{sc_id}")
        ela_time = (time.perf_counter() - t0) * 1000.0
        ela_metrics = compute_binary_metrics(gt_mask, ela_res.candidate_regions)

        # 2. Noise
        t0 = time.perf_counter()
        noise_res = noise_analyzer.analyze(Path(f"{sc_id}.{ext}"), img_bytes, {}, storage, f"noise_{sc_id}")
        noise_time = (time.perf_counter() - t0) * 1000.0
        noise_metrics = compute_binary_metrics(gt_mask, noise_res.candidate_regions)

        # 3. CMFD
        t0 = time.perf_counter()
        cmfd_res = cmfd_analyzer.analyze(Path(f"{sc_id}.{ext}"), img_bytes, {}, storage, f"cmfd_{sc_id}")
        cmfd_time = (time.perf_counter() - t0) * 1000.0
        cmfd_metrics = compute_binary_metrics(gt_mask, cmfd_res.candidate_regions)

        # 4. Consensus Fusion
        fusion_dict = {"ela": ela_res, "noise": noise_res, "cmfd": cmfd_res}
        t0 = time.perf_counter()
        fused_rois = fuse_candidate_regions(fusion_dict, iou_threshold=0.20)
        fusion_time = (time.perf_counter() - t0) * 1000.0
        fusion_metrics = compute_binary_metrics(gt_mask, fused_rois)

        record = {
            "scenario_id": sc_id,
            "attack_type": sc["attack_type"],
            "description": sc["description"],
            "ela_rois_count": len(ela_res.candidate_regions),
            "ela_latency_ms": round(ela_time, 2),
            "ela_precision": ela_metrics["precision"],
            "ela_recall": ela_metrics["recall"],
            "ela_f1": ela_metrics["f1"],
            "ela_iou": ela_metrics["iou"],
            "noise_rois_count": len(noise_res.candidate_regions),
            "noise_latency_ms": round(noise_time, 2),
            "noise_precision": noise_metrics["precision"],
            "noise_recall": noise_metrics["recall"],
            "noise_f1": noise_metrics["f1"],
            "noise_iou": noise_metrics["iou"],
            "cmfd_rois_count": len(cmfd_res.candidate_regions),
            "cmfd_latency_ms": round(cmfd_time, 2),
            "cmfd_precision": cmfd_metrics["precision"],
            "cmfd_recall": cmfd_metrics["recall"],
            "cmfd_f1": cmfd_metrics["f1"],
            "cmfd_iou": cmfd_metrics["iou"],
            "fused_rois_count": len(fused_rois),
            "fusion_latency_ms": round(fusion_time, 2),
            "fused_precision": fusion_metrics["precision"],
            "fused_recall": fusion_metrics["recall"],
            "fused_f1": fusion_metrics["f1"],
            "fused_iou": fusion_metrics["iou"],
        }
        results_detail.append(record)

    # Robustness Experiments (JPEG Quality Sweep on Spliced Image)
    print("\n[3/3] Executing Robustness Variations (JPEG Quality Sweep)...")
    robustness_records = []
    qualities = [50, 70, 85, 95]
    for q in qualities:
        # Recompress spliced composite at quality q
        spliced_raw = cv2.imdecode(np.frombuffer(spliced_bytes, np.uint8), cv2.IMREAD_COLOR)
        _, recomp_enc = cv2.imencode(".jpg", spliced_raw, [int(cv2.IMWRITE_JPEG_QUALITY), q])
        recomp_bytes = recomp_enc.tobytes()

        ela_res = ela_analyzer.analyze(Path(f"recomp_{q}.jpg"), recomp_bytes, {"quality": q, "scale": 15}, storage, f"recomp_{q}")
        m = compute_binary_metrics(spliced_gt, ela_res.candidate_regions)
        robustness_records.append({
            "attack_type": "Splicing",
            "perturbation": f"JPEG Quality {q}",
            "ela_rois": len(ela_res.candidate_regions),
            "precision": m["precision"],
            "recall": m["recall"],
            "f1": m["f1"],
            "iou": m["iou"],
        })

    # Save CSV outputs
    details_csv = out_dir / "classical_benchmark_details.csv"
    with open(details_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results_detail[0].keys()))
        writer.writeheader()
        writer.writerows(results_detail)

    robust_csv = out_dir / "robustness_metrics.csv"
    with open(robust_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(robustness_records[0].keys()))
        writer.writeheader()
        writer.writerows(robustness_records)

    # Save JSON summary
    summary_json = out_dir / "classical_benchmark_summary.json"
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "platform": "Q-TRACE Classical Forensics Engine",
        "num_scenarios": len(results_detail),
        "scenarios": results_detail,
        "robustness_sweep": robustness_records,
        "mean_latencies_ms": {
            "ela": round(float(np.mean([r["ela_latency_ms"] for r in results_detail])), 2),
            "noise": round(float(np.mean([r["noise_latency_ms"] for r in results_detail])), 2),
            "cmfd": round(float(np.mean([r["cmfd_latency_ms"] for r in results_detail])), 2),
            "fusion": round(float(np.mean([r["fusion_latency_ms"] for r in results_detail])), 2),
        }
    }
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n[OK] Results saved to {out_dir}:")
    print(f"  - {details_csv.name}")
    print(f"  - {robust_csv.name}")
    print(f"  - {summary_json.name}")
    print("Classical benchmark complete.")


if __name__ == "__main__":
    main()
