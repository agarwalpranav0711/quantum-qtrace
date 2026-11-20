"""Image Noise Analysis and Sensor Residual Consistency forensic analyzer."""

import io
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
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


class NoiseAnalyzer(ForensicTechnique):
    """Analyzes high-frequency sensor noise residuals and spatial variance consistency."""

    id: str = "noise"
    name: str = "Sensor Noise Inconsistency Analysis"
    version: str = "1.0.0"
    category: str = "Sensor Physics"
    description: (
        "Extracts high-frequency sensor noise residuals (PRNU/shot noise) via adaptive median filtering, "
        "computes spatial block-level variance distribution, and flags localized noise floor discrepancies."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {
        "block_size": 16,
        "filter_kernel": 3,
        "variance_threshold_sigma": 3.2,
    }
    limitations: List[str] = [
        "Heavily saturated highlights (pure white) and underexposed shadows (pure black) naturally exhibit suppressed sensor noise.",
        "Uniform downsampling or social media re-compression smooths high-frequency residuals across the entire image.",
        "Inconsistent noise variance may arise from depth-of-field blur or motion blur, not digital tampering.",
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
        block_size = int(params.get("block_size", 16))
        filter_kernel = int(params.get("filter_kernel", 3))
        variance_threshold_sigma = float(params.get("variance_threshold_sigma", 2.8))

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
                gray_arr = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2GRAY).astype(np.float32)
                height, width = gray_arr.shape

                # 1. Noise Extraction: N(x, y) = |I(x, y) - I_denoised(x, y)|
                # Using 3x3 median filtering to approximate the underlying scene radiance
                denoised = cv2.medianBlur(gray_arr.astype(np.uint8), filter_kernel).astype(np.float32)
                noise_residual = np.abs(gray_arr - denoised)

                # 2. Block-level noise variance estimation
                h_blocks = height // block_size
                w_blocks = width // block_size

                if h_blocks < 3 or w_blocks < 3:
                    raise ValueError(f"Image dimensions ({width}x{height}) too small for block size {block_size}.")

                variance_map = np.zeros((h_blocks, w_blocks), dtype=np.float32)
                mean_intensity_map = np.zeros((h_blocks, w_blocks), dtype=np.float32)

                for r in range(h_blocks):
                    for c in range(w_blocks):
                        y1, y2 = r * block_size, (r + 1) * block_size
                        x1, x2 = c * block_size, (c + 1) * block_size
                        block_residual = noise_residual[y1:y2, x1:x2]
                        variance_map[r, c] = np.var(block_residual)
                        mean_intensity_map[r, c] = np.mean(gray_arr[y1:y2, x1:x2])

                # Mask out extreme under- or over-exposed blocks where noise is non-linear
                valid_mask = (mean_intensity_map > 15) & (mean_intensity_map < 240)
                if np.sum(valid_mask) < (h_blocks * w_blocks * 0.2):
                    valid_mask = np.ones_like(variance_map, dtype=bool)

                valid_variances = variance_map[valid_mask]
                median_variance = float(np.median(valid_variances))
                mean_variance = float(np.mean(valid_variances))
                std_variance = float(np.std(valid_variances))
                iqr_variance = float(np.percentile(valid_variances, 75) - np.percentile(valid_variances, 25))

                metrics["block_size"] = block_size
                metrics["global_median_noise_variance"] = round(median_variance, 4)
                metrics["global_mean_noise_variance"] = round(mean_variance, 4)
                metrics["noise_variance_std"] = round(std_variance, 4)
                metrics["noise_variance_iqr"] = round(iqr_variance, 4)

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Sensor Noise Residual Profile",
                        description=(
                            f"Analyzed {h_blocks * w_blocks} spatial blocks ({block_size}x{block_size} px). "
                            f"Global median noise variance: {median_variance:.2f}, Std Dev: {std_variance:.2f}, IQR: {iqr_variance:.2f}."
                        ),
                        details={
                            "median_variance": median_variance,
                            "mean_variance": mean_variance,
                            "std_variance": std_variance,
                            "iqr_variance": iqr_variance,
                        },
                    )
                )

                # 3. Detect Anomalous Variance Discrepancies
                # Flag blocks where |variance - median| > threshold * std only when real noise variance exists
                if std_variance > 0.5:
                    high_thresh = median_variance + variance_threshold_sigma * std_variance
                    low_thresh = max(0.0, median_variance - variance_threshold_sigma * std_variance)
                    anomalous_blocks = ((variance_map > high_thresh) | (variance_map < low_thresh)) & valid_mask
                else:
                    high_thresh = median_variance + 1.0
                    anomalous_blocks = np.zeros_like(variance_map, dtype=bool)

                anomaly_count = int(np.sum(anomalous_blocks))
                metrics["anomalous_blocks_count"] = anomaly_count

                # 4. Generate Visual Noise Variance Heatmap
                # Normalize variance map to [0, 255] for visual artifact
                norm_var = np.clip((variance_map / (high_thresh + 1e-5)) * 255.0, 0, 255).astype(np.uint8)
                # Resize back to full image dimensions using nearest or bilinear
                full_heatmap = cv2.resize(norm_var, (width, height), interpolation=cv2.INTER_NEAREST)
                colorized_heatmap = cv2.applyColorMap(full_heatmap, cv2.COLORMAP_JET)
                colorized_rgb = cv2.cvtColor(colorized_heatmap, cv2.COLOR_BGR2RGB)

                # Alpha blend 50% with original image for investigator visual context
                blend = cv2.addWeighted(np.array(rgb_img), 0.55, colorized_rgb, 0.45, 0)
                heatmap_img = Image.fromarray(blend)

                # Save artifact
                art_buf = io.BytesIO()
                heatmap_img.save(art_buf, format="PNG")
                art_bytes = art_buf.getvalue()
                art_sha = compute_sha256_bytes(art_bytes)
                art_filename = f"noise_{analysis_id[:8]}_{block_size}px_{art_sha[:8]}.png"

                storage_service.store_file(
                    category="analysis",
                    filename=art_filename,
                    file_bytes=art_bytes,
                )

                artifacts.append(
                    ArtifactReference(
                        artifact_type="NOISE_HEATMAP",
                        stored_filename=art_filename,
                        description=f"Noise variance inconsistency heatmap ({block_size}x{block_size} px blocks) blended with original evidence",
                        mime_type="image/png",
                        sha256_hash=art_sha,
                    )
                )

                # 5. Extract Candidate RoIs from Connected Anomalous Blocks
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                    anomalous_blocks.astype(np.uint8), connectivity=8
                )

                roi_idx = 0
                for label in range(1, num_labels):
                    area = stats[label, cv2.CC_STAT_AREA]
                    if area >= 8:
                        bx = int(stats[label, cv2.CC_STAT_LEFT] * block_size)
                        by = int(stats[label, cv2.CC_STAT_TOP] * block_size)
                        bw = int(stats[label, cv2.CC_STAT_WIDTH] * block_size)
                        bh = int(stats[label, cv2.CC_STAT_HEIGHT] * block_size)

                        local_score = min(1.0, float(area / 12.0 + 0.35))
                        cx = int(centroids[label][0] * block_size)
                        cy = int(centroids[label][1] * block_size)

                        py1 = max(0, min(height - 4, cy - 2))
                        px1 = max(0, min(width - 4, cx - 2))
                        raw_4x4 = gray_arr[py1 : py1 + 4, px1 : px1 + 4].astype(np.uint8)
                        quantized_4x4 = (raw_4x4 >> 4).tolist()

                        roi_idx += 1
                        candidate_regions.append(
                            RegionOfInterest(
                                roi_id=f"NOISE-ROI-{roi_idx:02d}",
                                x=bx,
                                y=by,
                                width=bw,
                                height=bh,
                                score=round(local_score, 3),
                                contributing_techniques=["Sensor Noise Inconsistency Analysis"],
                                suggested_quantum_patch=quantized_4x4,
                            )
                        )

                if candidate_regions:
                    indicators.append(
                        FindingItem(
                            category=FindingCategory.INDICATOR,
                            title="Noise Floor Discrepancies Flagged",
                            description=(
                                f"Identified {len(candidate_regions)} region(s) where high-frequency noise variance "
                                f"significantly deviates from the global camera sensor baseline. "
                                "May indicate foreign element splicing, selective retouching, or local denoising."
                            ),
                            confidence=0.68,
                            details={"cluster_count": len(candidate_regions), "anomalous_blocks": anomaly_count},
                        )
                    )
                    hypotheses.append(
                        FindingItem(
                            category=FindingCategory.HYPOTHESIS,
                            title="Sensor Inconsistency / Spliced Patch",
                            description="Foreign graphic or patch from a different camera sensor model or noise profile.",
                            details={"roi_count": len(candidate_regions)},
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
                error_message=f"Noise analysis failed: {str(e)}",
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

