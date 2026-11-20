"""Consensus evidence fusion combining multi-technique forensic candidate regions."""

from typing import List, Dict
import numpy as np
from backend.app.forensics.schemas import RegionOfInterest, TechniqueResult


def calculate_iou(box1: RegionOfInterest, box2: RegionOfInterest) -> float:
    """Compute Intersection-over-Union (IoU) between two bounding boxes."""
    x1 = max(box1.x, box2.x)
    y1 = max(box1.y, box2.y)
    x2 = min(box1.x + box1.width, box2.x + box2.width)
    y2 = min(box1.y + box1.height, box2.y + box2.height)

    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    inter_area = inter_w * inter_h

    if inter_area == 0:
        return 0.0

    area1 = box1.width * box1.height
    area2 = box2.width * box2.height
    union_area = area1 + area2 - inter_area
    return float(inter_area / union_area) if union_area > 0 else 0.0


def fuse_candidate_regions(
    results: Dict[str, TechniqueResult],
    iou_threshold: float = 0.20,
) -> List[RegionOfInterest]:
    """
    Cluster and merge overlapping candidate RoIs from independent forensic techniques
    into unified Consensus Regions of Interest with cross-method validation.
    """
    all_rois: List[RegionOfInterest] = []
    for tech_id, res in results.items():
        if res.candidate_regions:
            all_rois.extend(res.candidate_regions)

    if not all_rois:
        return []

    # Sort by anomaly score descending
    all_rois.sort(key=lambda r: r.score, reverse=True)

    fused: List[RegionOfInterest] = []
    used = set()

    for i in range(len(all_rois)):
        if i in used:
            continue
        base_roi = all_rois[i]
        cluster = [base_roi]
        used.add(i)

        for j in range(i + 1, len(all_rois)):
            if j in used:
                continue
            cand_roi = all_rois[j]
            if calculate_iou(base_roi, cand_roi) >= iou_threshold:
                cluster.append(cand_roi)
                used.add(j)

        # Merge cluster into consensus region
        min_x = min(r.x for r in cluster)
        min_y = min(r.y for r in cluster)
        max_x = max(r.x + r.width for r in cluster)
        max_y = max(r.y + r.height for r in cluster)

        all_techniques = []
        for r in cluster:
            for t in r.contributing_techniques:
                if t not in all_techniques:
                    all_techniques.append(t)

        # Cross-validation score boost: regions flagged by multiple independent orthogonal techniques receive higher consensus
        base_score = float(np.mean([r.score for r in cluster]))
        mult_bonus = 0.15 * (len(all_techniques) - 1)
        consensus_score = min(0.99, base_score + mult_bonus)

        # Best quantum patch (from highest scoring member)
        best_patch = cluster[0].suggested_quantum_patch

        fused.append(
            RegionOfInterest(
                roi_id=f"CONSENSUS-ROI-{len(fused) + 1:02d}",
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y,
                score=round(consensus_score, 3),
                contributing_techniques=all_techniques,
                suggested_quantum_patch=best_patch,
            )
        )

    return fused

