"""Copy-Move Forgery Detection (CMFD) forensic analyzer using SIFT keypoint clustering."""

import io
import time
import math
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image
import cv2

from backend.app.forensics.base import ForensicTechnique
from backend.app.forensics.schemas import (
    TechniqueResult,
    ForensicStatus,
    FindingCategory,
    FindingItem,
    ArtifactReference,
    RegionOfInterest,
)
from backend.app.storage.service import StorageService
from backend.app.services.integrity import compute_sha256_bytes


class CopyMoveAnalyzer(ForensicTechnique):
    """Detects duplicated image regions using SIFT/ORB keypoints and spatial vector clustering."""

    id: str = "copy_move"
    name: str = "Copy-Move Forgery Detection (CMFD)"
    version: str = "1.0.0"
    category: str = "Geometric & Spatial"
    description: (
        "Extracts scale- and rotation-invariant feature keypoints (SIFT), performs ratio-filtered "
        "k-NN descriptor matching, applies minimum spatial distance constraints, and clusters "
        "parallel displacement vectors to detect cloned damage or duplicated patches."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {
        "algorithm": "SIFT",            # SIFT or ORB
        "ratio_threshold": 0.68,        # Lowe's ratio test
        "min_spatial_distance": 35.0,   # Minimum pixel distance between candidate clones
        "min_cluster_size": 3,          # Minimum parallel vectors to constitute a candidate clone
        "vector_angle_tolerance_deg": 15.0,
    }
    limitations: List[str] = [
        "Smooth, textureless surfaces (e.g. unpainted panels, clear skies, polished hoods) yield zero keypoints.",
        "Naturally repetitive physical structures (e.g. vehicle grilles, headlights, tire treads, building windows) "
        "frequently produce false positive matches.",
        "Heavily blurred, highly compressed, or rotated duplicates may fail keypoint descriptor matching.",
    ]

    def analyze(
        self,
        image_path: Path,
        image_bytes: bytes,
        parameters: Dict[str, Any],
        storage_service: StorageService,
        analysis_id: str,
    ) -> TechniqueResult:
        start_time = time.perf_counter()
        params = {**self.default_parameters, **parameters}
        algo_choice = str(params.get("algorithm", "SIFT")).upper()
        ratio_thresh = float(params.get("ratio_threshold", 0.68))
        min_dist = float(params.get("min_spatial_distance", 35.0))
        min_cluster = int(params.get("min_cluster_size", 3))
        angle_tol = float(params.get("vector_angle_tolerance_deg", 15.0))

        observations: List[FindingItem] = []
        indicators: List[FindingItem] = []
        hypotheses: List[FindingItem] = []
        metrics: Dict[str, Any] = {}
        candidate_regions: List[RegionOfInterest] = []
        artifacts: List[ArtifactReference] = []
        warnings: List[str] = []

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                rgb_img = img.convert("RGB")
                orig_arr = np.array(rgb_img)
                gray = cv2.cvtColor(orig_arr, cv2.COLOR_RGB2GRAY)
                height, width = gray.shape

                # 1. Feature Detection & Description
                use_sift = (algo_choice == "SIFT") and hasattr(cv2, "SIFT_create")
                if use_sift:
                    detector = cv2.SIFT_create(nfeatures=2000)
                else:
                    detector = cv2.ORB_create(nfeatures=2000)
                    warnings.append("Using ORB feature detector fallback instead of SIFT.")

                keypoints, descriptors = detector.detectAndCompute(gray, None)
                kp_count = len(keypoints) if keypoints is not None else 0
                metrics["keypoint_count"] = kp_count
                metrics["feature_detector"] = "SIFT" if use_sift else "ORB"

                if kp_count < 10 or descriptors is None:
                    observations.append(
                        FindingItem(
                            category=FindingCategory.OBSERVATION,
                            title="Insufficient Image Texture",
                            description=f"Extracted only {kp_count} keypoint(s). Surface lacks sufficient texture for copy-move matching.",
                            details={"keypoints": kp_count},
                        )
                    )
                    elapsed = (time.perf_counter() - start_time) * 1000.0
                    return TechniqueResult(
                        technique_id=self.id,
                        technique_name=self.name,
                        version=self.version,
                        category=self.category,
                        status=ForensicStatus.INCONCLUSIVE,
                        execution_time_ms=elapsed,
                        parameters_used=params,
                        observations=observations,
                        metrics=metrics,
                        limitations=self.limitations,
                        warnings=warnings,
                    )

                # 2. 2-NN Descriptor Matching with Lowe's Ratio Test
                # For an image compared to itself, nearest neighbor (k=1) is the identical keypoint itself!
                # We request k=3 or k=4 neighbors to find distinct non-identical matches.
                if use_sift:
                    matcher = cv2.BFMatcher(cv2.NORM_L2)
                else:
                    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

                raw_matches = matcher.knnMatch(descriptors, descriptors, k=4)

                matched_pairs: List[Tuple[cv2.KeyPoint, cv2.KeyPoint, float, float]] = []
                seen_pairs = set()

                for m_group in raw_matches:
                    if len(m_group) < 3:
                        continue
                    # First match m_group[0] is self-match (distance == 0.0)
                    # Second match m_group[1] is candidate twin
                    # Third match m_group[2] is denominator for ratio test
                    candidate = m_group[1]
                    denominator = m_group[2]

                    if candidate.distance < (ratio_thresh * denominator.distance):
                        q_idx = candidate.queryIdx
                        t_idx = candidate.trainIdx
                        if q_idx == t_idx:
                            continue

                        pair_key = (min(q_idx, t_idx), max(q_idx, t_idx))
                        if pair_key in seen_pairs:
                            continue
                        seen_pairs.add(pair_key)

                        pt1 = keypoints[q_idx].pt
                        pt2 = keypoints[t_idx].pt

                        dx = pt2[0] - pt1[0]
                        dy = pt2[1] - pt1[1]
                        dist = math.hypot(dx, dy)

                        # Enforce minimum spatial distance to eliminate adjacent pixel matches
                        if dist >= min_dist:
                            angle = math.degrees(math.atan2(dy, dx)) % 180.0  # Direction invariant
                            matched_pairs.append((keypoints[q_idx], keypoints[t_idx], dist, angle))

                metrics["raw_matched_pairs"] = len(matched_pairs)

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Keypoint Feature Matching",
                        description=(
                            f"Detected {kp_count} {metrics['feature_detector']} keypoints. "
                            f"Identified {len(matched_pairs)} candidate duplicate pair(s) satisfying ratio test "
                            f"(< {ratio_thresh}) and spatial distance constraint (> {min_dist} px)."
                        ),
                        details={
                            "keypoints": kp_count,
                            "matched_pairs": len(matched_pairs),
                            "ratio_threshold": ratio_thresh,
                            "min_distance": min_dist,
                        },
                    )
                )

                # 3. Spatial Displacement Vector Clustering
                # Real copy-move operations replicate a group of points with approximately identical displacement vectors
                clusters: List[List[Tuple[cv2.KeyPoint, cv2.KeyPoint, float, float]]] = []
                used_indices = set()

                for i in range(len(matched_pairs)):
                    if i in used_indices:
                        continue
                    current_cluster = [matched_pairs[i]]
                    _, _, d1, a1 = matched_pairs[i]

                    for j in range(i + 1, len(matched_pairs)):
                        if j in used_indices:
                            continue
                        _, _, d2, a2 = matched_pairs[j]

                        # Check distance and angle consistency
                        dist_diff = abs(d1 - d2) / max(d1, d2)
                        angle_diff = abs(a1 - a2)
                        if angle_diff > 90:
                            angle_diff = 180 - angle_diff

                        if dist_diff < 0.20 and angle_diff < angle_tol:
                            current_cluster.append(matched_pairs[j])
                            used_indices.add(j)

                    if len(current_cluster) >= min_cluster:
                        clusters.append(current_cluster)
                        used_indices.add(i)

                metrics["consistent_clusters_count"] = len(clusters)

                # 4. Generate Visual Match Overlay Artifact
                vis_img = orig_arr.copy()
                colors = [(0, 242, 254), (16, 185, 129), (244, 63, 94), (129, 140, 248), (245, 158, 11)]  # RGB palette

                roi_idx = 0
                for c_idx, cluster in enumerate(clusters):
                    color = colors[c_idx % len(colors)]
                    src_pts = []
                    dst_pts = []

                    for kp1, kp2, _, _ in cluster:
                        p1 = (int(round(kp1.pt[0])), int(round(kp1.pt[1])))
                        p2 = (int(round(kp2.pt[0])), int(round(kp2.pt[1])))
                        src_pts.append(p1)
                        dst_pts.append(p2)

                        # Draw connection vector line
                        cv2.line(vis_img, p1, p2, color, 2, cv2.LINE_AA)
                        cv2.circle(vis_img, p1, 4, color, -1, cv2.LINE_AA)
                        cv2.circle(vis_img, p2, 4, (255, 255, 255), 1, cv2.LINE_AA)

                    # Bounding boxes around source cluster and target cluster
                    src_arr = np.array(src_pts)
                    dst_arr = np.array(dst_pts)

                    sx, sy, sw, sh = cv2.boundingRect(src_arr)
                    tx, ty, tw, th = cv2.boundingRect(dst_arr)

                    # Add padding to bounding box
                    pad = 12
                    sx, sy = max(0, sx - pad), max(0, sy - pad)
                    sw, sh = min(width - sx, sw + 2 * pad), min(height - sy, sh + 2 * pad)
                    tx, ty = max(0, tx - pad), max(0, ty - pad)
                    tw, th = min(width - tx, tw + 2 * pad), min(height - ty, th + 2 * pad)

                    # Draw rectangles
                    cv2.rectangle(vis_img, (sx, sy), (sx + sw, sy + sh), color, 2)
                    cv2.rectangle(vis_img, (tx, ty), (tx + tw, ty + th), (255, 255, 255), 2)

                    # Extract 4x4 quantum patch from source cluster centroid
                    scx, scy = int(sx + sw // 2), int(sy + sh // 2)
                    py1 = max(0, min(height - 4, scy - 2))
                    px1 = max(0, min(width - 4, scx - 2))
                    quantized_4x4 = (gray[py1 : py1 + 4, px1 : px1 + 4] >> 4).tolist()

                    roi_idx += 1
                    confidence_score = min(1.0, float(len(cluster) / 10.0 + 0.45))
                    candidate_regions.append(
                        RegionOfInterest(
                            roi_id=f"CMFD-SRC-{roi_idx:02d}",
                            x=sx,
                            y=sy,
                            width=sw,
                            height=sh,
                            score=round(confidence_score, 3),
                            contributing_techniques=["Copy-Move Forgery Detection (CMFD)"],
                            suggested_quantum_patch=quantized_4x4,
                        )
                    )
                    candidate_regions.append(
                        RegionOfInterest(
                            roi_id=f"CMFD-DST-{roi_idx:02d}",
                            x=tx,
                            y=ty,
                            width=tw,
                            height=th,
                            score=round(confidence_score, 3),
                            contributing_techniques=["Copy-Move Forgery Detection (CMFD)"],
                            suggested_quantum_patch=(gray[max(0, min(height - 4, ty + th // 2 - 2)) : max(0, min(height - 4, ty + th // 2 - 2)) + 4, max(0, min(width - 4, tx + tw // 2 - 2)) : max(0, min(width - 4, tx + tw // 2 - 2)) + 4] >> 4).tolist(),
                        )
                    )

                # Save match overlay artifact
                art_img = Image.fromarray(vis_img)
                art_buf = io.BytesIO()
                art_img.save(art_buf, format="PNG")
                art_bytes = art_buf.getvalue()
                art_sha = compute_sha256_bytes(art_bytes)
                art_filename = f"cmfd_{analysis_id[:8]}_{metrics['feature_detector'].lower()}_{art_sha[:8]}.png"

                storage_service.store_file(
                    category="analysis",
                    filename=art_filename,
                    file_bytes=art_bytes,
                )

                artifacts.append(
                    ArtifactReference(
                        artifact_type="CMFD_MATCHES",
                        stored_filename=art_filename,
                        description=(
                            f"Copy-Move keypoint vector visualization ({metrics['feature_detector']}, "
                            f"{len(matched_pairs)} matched pairs, {len(clusters)} coherent clusters)"
                        ),
                        mime_type="image/png",
                        sha256_hash=art_sha,
                    )
                )

                if clusters:
                    indicators.append(
                        FindingItem(
                            category=FindingCategory.INDICATOR,
                            title="Cloned Image Region Clusters Detected",
                            description=(
                                f"Detected {len(clusters)} spatially coherent keypoint vector cluster(s) with parallel displacement. "
                                "Indicates candidate duplicate panels, cloned vehicle damage, or duplicated textural elements."
                            ),
                            confidence=0.78,
                            details={"cluster_count": len(clusters), "total_matched_pairs": len(matched_pairs)},
                        )
                    )
                    hypotheses.append(
                        FindingItem(
                            category=FindingCategory.HYPOTHESIS,
                            title="Copy-Move Forgery / Damage Duplication",
                            description="Suspected stamp or cloning tool duplication of dent, scratch, or textural feature.",
                            details={"cluster_count": len(clusters)},
                        )
                    )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return TechniqueResult(
                technique_id=self.id,
                technique_name=self.name,
                version=self.version,
                category=self.category,
                status=ForensicStatus.ANALYSIS_FAILED,
                execution_time_ms=elapsed,
                parameters_used=params,
                error_message=f"Copy-Move analysis failed: {str(e)}",
                limitations=self.limitations,
            )

        elapsed = (time.perf_counter() - start_time) * 1000.0
        status = ForensicStatus.POTENTIAL_INDICATOR_DETECTED if indicators else ForensicStatus.NO_ANOMALY_DETECTED

        return TechniqueResult(
            technique_id=self.id,
            technique_name=self.name,
            version=self.version,
            category=self.category,
            status=status,
            execution_time_ms=elapsed,
            parameters_used=params,
            observations=observations,
            indicators=indicators,
            hypotheses=hypotheses,
            metrics=metrics,
            candidate_regions=candidate_regions,
            artifacts=artifacts,
            limitations=self.limitations,
            warnings=warnings,
        )

