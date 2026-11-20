"""Error Level Analysis (ELA) forensic analyzer."""

import io
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageChops, ImageEnhance
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


class ErrorLevelAnalyzer(ForensicTechnique):
    """Analyzes rate-distortion compression error by re-compressing at known JPEG quality."""

    id: str = "ela"
    name: str = "Error Level Analysis (ELA)"
    version: str = "1.0.0"
    category: str = "Compression Physics"
    description: (
        "Re-encodes image at a reference JPEG quality grid (default: 95) and computes localized "
        "re-compression error deltas to detect regions with conflicting compression histories or foreign splices."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {
        "quality": 95,
        "scale": 15,
        "edge_masking": True,
        "roi_threshold_std": 2.5,
    }
    limitations: List[str] = [
        "Natural high-contrast edges (e.g. car panel seams, chrome trim) inherently yield higher high-frequency DCT residuals.",
        "Repeated uniform re-saving of an image progressively elevates the error floor, reducing ELA contrast.",
        "ELA is non-uniform across smooth vs. textured surfaces; high error is NOT synonymous with forgery.",
        "Lossless images (PNG/TIFF) do not contain native JPEG quantization history; resaving simulates a first-generation JPEG encoding.",
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
        quality = int(params.get("quality", 95))
        scale = int(params.get("scale", 15))
        edge_masking = bool(params.get("edge_masking", True))
        roi_threshold_std = float(params.get("roi_threshold_std", 2.5))

        observations: List[FindingItem] = []
        indicators: List[FindingItem] = []
        hypotheses: List[FindingItem] = []
        metrics: Dict[str, Any] = {}
        candidate_regions: List[RegionOfInterest] = []
        artifacts: List[ArtifactReference] = []
        warnings: List[str] = []

        try:
            # 1. Load original image
            with Image.open(io.BytesIO(image_bytes)) as orig_img:
                is_jpeg = (orig_img.format == "JPEG")
                if not is_jpeg:
                    warnings.append(
                        f"Original image format is {orig_img.format}, not JPEG. "
                        "Re-compression produces first-generation DCT residuals rather than differential historical error."
                    )

                # Ensure RGB mode for comparison
                rgb_orig = orig_img.convert("RGB")
                width, height = rgb_orig.size

                # 2. Re-encode to JPEG in-memory buffer at specified quality
                resave_buffer = io.BytesIO()
                rgb_orig.save(resave_buffer, "JPEG", quality=quality)
                resave_buffer.seek(0)
                resaved_img = Image.open(resave_buffer)

                # 3. Calculate absolute difference image: E(x, y) = |I_orig - I_resaved|
                diff_img = ImageChops.difference(rgb_orig, resaved_img)

                # Convert to numpy arrays
                diff_arr = np.array(diff_img, dtype=np.float32)  # Shape (H, W, 3)
                gray_diff = np.mean(diff_arr, axis=2)            # Shape (H, W)

                # Calculate statistical error metrics
                mean_error = float(np.mean(gray_diff))
                max_error = float(np.max(gray_diff))
                std_error = float(np.std(gray_diff))
                p95_error = float(np.percentile(gray_diff, 95))
                high_error_ratio = float(np.mean(gray_diff > (mean_error + 2 * std_error)))

                metrics["quality_setting"] = quality
                metrics["amplification_scale"] = scale
                metrics["mean_error"] = round(mean_error, 4)
                metrics["max_error"] = round(max_error, 4)
                metrics["std_error"] = round(std_error, 4)
                metrics["p95_error"] = round(p95_error, 4)
                metrics["high_error_pixel_ratio"] = round(high_error_ratio, 4)

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Re-Compression Error Distribution",
                        description=(
                            f"Re-encoded at JPEG Quality {quality}. Mean error: {mean_error:.2f}/255, "
                            f"Std Dev: {std_error:.2f}, 95th Percentile: {p95_error:.2f}."
                        ),
                        details={
                            "quality": quality,
                            "mean_error": mean_error,
                            "std_error": std_error,
                            "p95_error": p95_error,
                        },
                    )
                )

                # 4. Generate enhanced ELA visualization image
                # ELA(x, y) = min(255, scale * E(x, y))
                enhanced_arr = np.clip(diff_arr * scale, 0, 255).astype(np.uint8)
                enhanced_img = Image.fromarray(enhanced_arr)

                # Save enhanced artifact to storage
                artifact_buf = io.BytesIO()
                enhanced_img.save(artifact_buf, format="PNG")
                artifact_bytes = artifact_buf.getvalue()
                artifact_sha = compute_sha256_bytes(artifact_bytes)
                artifact_filename = f"ela_{analysis_id[:8]}_{quality}q_{artifact_sha[:8]}.png"

                target_path = storage_service.store_file(
                    category="analysis",
                    filename=artifact_filename,
                    file_bytes=artifact_bytes,
                )

                artifacts.append(
                    ArtifactReference(
                        artifact_type="ELA_HEATMAP",
                        stored_filename=artifact_filename,
                        description=f"Error Level Analysis visualization enhanced at scale {scale}x (JPEG Quality {quality})",
                        mime_type="image/png",
                        sha256_hash=artifact_sha,
                    )
                )

                # 5. Candidate Region of Interest (RoI) Extraction with Edge Masking
                # Compute Sobel edge mask on original grayscale to filter out natural high-contrast edges
                orig_gray = cv2.cvtColor(np.array(rgb_orig), cv2.COLOR_RGB2GRAY)
                if edge_masking:
                    sobelx = cv2.Sobel(orig_gray, cv2.CV_64F, 1, 0, ksize=3)
                    sobely = cv2.Sobel(orig_gray, cv2.CV_64F, 0, 1, ksize=3)
                    edge_mag = np.sqrt(sobelx**2 + sobely**2)
                    edge_threshold = np.percentile(edge_mag, 85)
                    non_edge_mask = (edge_mag < edge_threshold)
                else:
                    non_edge_mask = np.ones_like(orig_gray, dtype=bool)

                # Downsample error into 16x16 blocks
                block_size = 16
                h_blocks = height // block_size
                w_blocks = width // block_size

                if h_blocks > 2 and w_blocks > 2:
                    block_errors = np.zeros((h_blocks, w_blocks), dtype=np.float32)
                    for r in range(h_blocks):
                        for c in range(w_blocks):
                            y1, y2 = r * block_size, (r + 1) * block_size
                            x1, x2 = c * block_size, (c + 1) * block_size
                            b_mask = non_edge_mask[y1:y2, x1:x2]
                            if np.sum(b_mask) > (block_size * block_size * 0.3):
                                block_errors[r, c] = np.mean(gray_diff[y1:y2, x1:x2][b_mask])
                            else:
                                block_errors[r, c] = 0.0

                    # Anomaly threshold: mean + roi_threshold_std * std, with absolute minimum floor of 14.0
                    b_mean = np.mean(block_errors[block_errors > 0]) if np.any(block_errors > 0) else 0.0
                    b_std = np.std(block_errors[block_errors > 0]) if np.any(block_errors > 0) else 1.0
                    anomaly_threshold = max(14.0, b_mean + roi_threshold_std * b_std)

                    anomalous_blocks = (block_errors > anomaly_threshold).astype(np.uint8)

                    # Find connected components of anomalous blocks
                    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                        anomalous_blocks, connectivity=8
                    )

                    # Collect candidate RoIs (min 2 connected blocks)
                    roi_count = 0
                    for label in range(1, num_labels):
                        area = stats[label, cv2.CC_STAT_AREA]
                        if area >= 2:
                            bx = int(stats[label, cv2.CC_STAT_LEFT] * block_size)
                            by = int(stats[label, cv2.CC_STAT_TOP] * block_size)
                            bw = int(stats[label, cv2.CC_STAT_WIDTH] * block_size)
                            bh = int(stats[label, cv2.CC_STAT_HEIGHT] * block_size)

                            # Calculate local score
                            local_score = min(1.0, float(stats[label, cv2.CC_STAT_AREA] / 10.0 + 0.4))
                            cx = int(centroids[label][0] * block_size)
                            cy = int(centroids[label][1] * block_size)

                            # Extract 4x4 quantum patch from centroid
                            # Clamped inside boundaries
                            py1 = max(0, min(height - 4, cy - 2))
                            px1 = max(0, min(width - 4, cx - 2))
                            raw_4x4 = orig_gray[py1 : py1 + 4, px1 : px1 + 4]
                            # Quantize 8-bit [0, 255] down to 4-bit [0, 15] for NEQR register
                            quantized_4x4 = (raw_4x4 >> 4).tolist()

                            roi_count += 1
                            candidate_regions.append(
                                RegionOfInterest(
                                    roi_id=f"ELA-ROI-{roi_count:02d}",
                                    x=bx,
                                    y=by,
                                    width=bw,
                                    height=bh,
                                    score=round(local_score, 3),
                                    contributing_techniques=["Error Level Analysis (ELA)"],
                                    suggested_quantum_patch=quantized_4x4,
                                )
                            )

                    if candidate_regions:
                        indicators.append(
                            FindingItem(
                                category=FindingCategory.INDICATOR,
                                title="Localized High-Error Clusters Detected",
                                description=(
                                    f"Detected {len(candidate_regions)} localized non-edge block cluster(s) with re-compression error "
                                    f"exceeding {roi_threshold_std} standard deviations from baseline. "
                                    "Suggests potential foreign patch insertion, differing save history, or localized retouching."
                                ),
                                confidence=0.72,
                                details={"cluster_count": len(candidate_regions), "anomaly_threshold": round(float(anomaly_threshold), 2)},
                            )
                        )
                        hypotheses.append(
                            FindingItem(
                                category=FindingCategory.HYPOTHESIS,
                                title="Compression Inconsistency / Spliced Content",
                                description="High-error clusters may represent elements imported from a source saved at higher compression quality.",
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
                error_message=f"ELA processing failed: {str(e)}",
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

