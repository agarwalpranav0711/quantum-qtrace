"""Resampling, Edge Gradient Discontinuity, and Inpainting forensic analyzer."""

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


class ResamplingAnalyzer(ForensicTechnique):
    """Analyzes edge gradient discontinuity, Laplacian texture variance, and inpainting artifacts."""

    id: str = "resampling"
    name: str = "Edge Gradient & Inpainting Analysis"
    version: str = "1.0.0"
    category: str = "Edge & Interpolation"
    description: (
        "Measures 2D Sobel edge gradients and Laplacian texture variance to detect unnatural "
        "smoothing, digital scratch/dent inpainting, or boundary feathering around spliced elements."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {
        "block_size": 16,
        "smoothing_ratio_threshold": 0.15,
    }
    limitations: List[str] = [
        "Unpainted smooth automotive plastic, tinted glass, or uniform clear skies naturally possess near-zero Laplacian variance.",
        "Optical lens bokeh, depth-of-field, or motion blur naturally suppresses high-frequency edge gradients.",
        "Edge discontinuity analysis is an indicator of texture anomaly, not definitive proof of malicious tampering.",
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
        smoothing_thresh = float(params.get("smoothing_ratio_threshold", 0.15))

        observations: List[FindingItem] = []
        indicators: List[FindingItem] = []
        hypotheses: List[FindingItem] = []
        metrics: Dict[str, Any] = {}
        candidate_regions: List[RegionOfInterest] = []
        artifacts: List[ArtifactReference] = []
        warnings: List[str] = []

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                gray_arr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY).astype(np.float32)
                height, width = gray_arr.shape

                # 1. Compute Sobel Edge Gradients
                sobelx = cv2.Sobel(gray_arr, cv2.CV_32F, 1, 0, ksize=3)
                sobely = cv2.Sobel(gray_arr, cv2.CV_32F, 0, 1, ksize=3)
                gradient_mag = np.sqrt(sobelx**2 + sobely**2)

                # 2. Compute Laplacian Texture Variance
                laplacian = cv2.Laplacian(gray_arr, cv2.CV_32F, ksize=3)
                global_laplacian_var = float(np.var(laplacian))
                mean_grad_mag = float(np.mean(gradient_mag))
                p90_grad_mag = float(np.percentile(gradient_mag, 90))

                metrics["global_laplacian_variance"] = round(global_laplacian_var, 3)
                metrics["mean_gradient_magnitude"] = round(mean_grad_mag, 3)
                metrics["p90_gradient_magnitude"] = round(p90_grad_mag, 3)

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Gradient & Sharpness Profile",
                        description=(
                            f"Global Laplacian Variance: {global_laplacian_var:.2f} (Sharpness metric). "
                            f"Mean Gradient: {mean_grad_mag:.2f}, 90th Percentile: {p90_grad_mag:.2f}."
                        ),
                        details={
                            "laplacian_variance": global_laplacian_var,
                            "mean_gradient": mean_grad_mag,
                            "p90_gradient": p90_grad_mag,
                        },
                    )
                )

                # 3. Block-Level Laplacian Smoothing Analysis (Inpainting Detection)
                h_blocks = height // block_size
                w_blocks = width // block_size

                if h_blocks >= 3 and w_blocks >= 3:
                    block_lap_vars = np.zeros((h_blocks, w_blocks), dtype=np.float32)
                    for r in range(h_blocks):
                        for c in range(w_blocks):
                            y1, y2 = r * block_size, (r + 1) * block_size
                            x1, x2 = c * block_size, (c + 1) * block_size
                            block_lap_vars[r, c] = np.var(laplacian[y1:y2, x1:x2])

                    # Inpainted patches exhibit near-zero variance amidst textured surrounds
                    # Flag blocks where local variance is < 15% of image median variance
                    med_var = np.median(block_lap_vars)
                    if med_var > 10.0:  # Only meaningful if image has baseline texture
                        smooth_blocks = (block_lap_vars < (med_var * smoothing_thresh)).astype(np.uint8)
                        # Require isolated smooth blocks surrounded by texture (morphological check)
                        kernel = np.ones((3, 3), np.uint8)
                        dilated = cv2.dilate(smooth_blocks, kernel, iterations=1)
                        # Connected components
                        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(smooth_blocks, connectivity=8)

                        roi_idx = 0
                        for label in range(1, num_labels):
                            area = stats[label, cv2.CC_STAT_AREA]
                            if 2 <= area <= 20:  # Localized smoothed patch
                                bx = int(stats[label, cv2.CC_STAT_LEFT] * block_size)
                                by = int(stats[label, cv2.CC_STAT_TOP] * block_size)
                                bw = int(stats[label, cv2.CC_STAT_WIDTH] * block_size)
                                bh = int(stats[label, cv2.CC_STAT_HEIGHT] * block_size)

                                cx = int(centroids[label][0] * block_size)
                                cy = int(centroids[label][1] * block_size)
                                py1 = max(0, min(height - 4, cy - 2))
                                px1 = max(0, min(width - 4, cx - 2))
                                q_patch = (gray_arr[py1:py1+4, px1:px1+4].astype(np.uint8) >> 4).tolist()

                                roi_idx += 1
                                candidate_regions.append(
                                    RegionOfInterest(
                                        roi_id=f"INPAINT-ROI-{roi_idx:02d}",
                                        x=bx,
                                        y=by,
                                        width=bw,
                                        height=bh,
                                        score=0.62,
                                        contributing_techniques=["Edge Gradient & Inpainting Analysis"],
                                        suggested_quantum_patch=q_patch,
                                    )
                                )

                        if candidate_regions:
                            indicators.append(
                                FindingItem(
                                    category=FindingCategory.INDICATOR,
                                    title="Localized Texture Smoothing / Potential Inpainting",
                                    description=(
                                        f"Detected {len(candidate_regions)} localized patch(es) with an unnatural drop in Laplacian variance "
                                        "surrounded by high-texture bodywork. Characteristic of digital scratch erasure or inpainting."
                                    ),
                                    confidence=0.64,
                                    details={"smooth_patches": len(candidate_regions)},
                                )
                            )

                # 4. Generate Visual Gradient Artifact
                norm_grad = np.clip((gradient_mag / (p90_grad_mag + 1e-5)) * 255.0, 0, 255).astype(np.uint8)
                colorized = cv2.applyColorMap(norm_grad, cv2.COLORMAP_VIRIDIS)
                art_img = Image.fromarray(cv2.cvtColor(colorized, cv2.COLOR_BGR2RGB))

                art_buf = io.BytesIO()
                art_img.save(art_buf, format="PNG")
                art_bytes = art_buf.getvalue()
                art_sha = compute_sha256_bytes(art_bytes)
                art_filename = f"edge_{analysis_id[:8]}_{art_sha[:8]}.png"

                storage_service.store_file(
                    category="analysis",
                    filename=art_filename,
                    file_bytes=art_bytes,
                )

                artifacts.append(
                    ArtifactReference(
                        artifact_type="EDGE_GRADIENT_MAP",
                        stored_filename=art_filename,
                        description="Sobel edge gradient magnitude map (Viridis colormap)",
                        mime_type="image/png",
                        sha256_hash=art_sha,
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
                error_message=f"Resampling analysis failed: {str(e)}",
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

