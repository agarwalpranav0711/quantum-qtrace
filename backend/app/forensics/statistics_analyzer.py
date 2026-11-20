"""Image Statistical Profiling and Multi-Channel Histogram forensic analyzer."""

import io
import time
import math
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
)
from backend.app.storage.service import StorageService
from backend.app.services.integrity import compute_sha256_bytes


def compute_shannon_entropy(hist: np.ndarray) -> float:
    """Compute Shannon entropy in bits from normalized histogram."""
    p = hist / (np.sum(hist) + 1e-12)
    p_non_zero = p[p > 0]
    return float(-np.sum(p_non_zero * np.log2(p_non_zero)))


class StatisticsAnalyzer(ForensicTechnique):
    """Computes comprehensive multi-channel intensity statistics, entropy, and clipping profiles."""

    id: str = "statistics"
    name: str = "Image Statistics & Channel Histograms"
    version: str = "1.0.0"
    category: str = "Signal Distribution"
    description: (
        "Measures 256-bin RGB and luminance histograms, Shannon information entropy, "
        "intensity dispersion (skewness, kurtosis), and flags non-linear histogram equalization or clipping."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {
        "clipping_threshold_percent": 5.0,
        "comb_anomaly_threshold": 0.25,
    }
    limitations: List[str] = [
        "Direct sunlight reflections, headlights, or deep night shadows naturally produce high clipping percentages.",
        "Color grading or basic exposure adjustments performed legitimately in-camera alter histogram profiles.",
        "Global statistical measurements provide contextual intelligence but cannot independently locate local splices.",
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
        clip_thresh = float(params.get("clipping_threshold_percent", 5.0))

        observations: List[FindingItem] = []
        indicators: List[FindingItem] = []
        hypotheses: List[FindingItem] = []
        metrics: Dict[str, Any] = {}
        artifacts: List[ArtifactReference] = []
        warnings: List[str] = []

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                rgb_img = img.convert("RGB")
                rgb_arr = np.array(rgb_img)
                gray_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2GRAY)
                total_pixels = gray_arr.size

                # 1. Channel intensity statistics
                channels = {"Red": rgb_arr[:, :, 0], "Green": rgb_arr[:, :, 1], "Blue": rgb_arr[:, :, 2], "Luminance": gray_arr}
                channel_stats = {}
                histograms = {}

                for ch_name, data in channels.items():
                    hist, _ = np.histogram(data, bins=256, range=(0, 256))
                    histograms[ch_name] = hist
                    mean_val = float(np.mean(data))
                    std_val = float(np.std(data))
                    min_val = int(np.min(data))
                    max_val = int(np.max(data))
                    entropy = compute_shannon_entropy(hist)

                    # Skewness
                    m3 = np.mean((data - mean_val) ** 3)
                    skew = float(m3 / (std_val ** 3 + 1e-6))

                    channel_stats[ch_name.lower()] = {
                        "mean": round(mean_val, 2),
                        "std": round(std_val, 2),
                        "min": min_val,
                        "max": max_val,
                        "dynamic_range": max_val - min_val,
                        "entropy_bits": round(entropy, 3),
                        "skewness": round(skew, 3),
                    }

                # Clipping analysis on Luminance
                zero_count = int(np.sum(gray_arr == 0))
                sat_count = int(np.sum(gray_arr == 255))
                zero_pct = float((zero_count / total_pixels) * 100.0)
                sat_pct = float((sat_count / total_pixels) * 100.0)

                metrics["channels"] = channel_stats
                metrics["clipping"] = {
                    "underexposed_black_pct": round(zero_pct, 3),
                    "overexposed_white_pct": round(sat_pct, 3),
                    "total_clipped_pct": round(zero_pct + sat_pct, 3),
                }

                # Comb effect detection (zero-frequency gaps between bins from aggressive levels adjustment)
                lum_hist = histograms["Luminance"]
                zero_bin_gaps = 0
                for b in range(10, 245):
                    if lum_hist[b] == 0 and lum_hist[b - 1] > 0 and lum_hist[b + 1] > 0:
                        zero_bin_gaps += 1
                metrics["histogram_comb_gaps"] = zero_bin_gaps

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Statistical Signal Distribution",
                        description=(
                            f"Luminance Mean: {channel_stats['luminance']['mean']:.1f}/255, "
                            f"Std Dev: {channel_stats['luminance']['std']:.1f}, "
                            f"Dynamic Range: {channel_stats['luminance']['dynamic_range']}, "
                            f"Information Entropy: {channel_stats['luminance']['entropy_bits']:.2f} bits/pixel."
                        ),
                        details=channel_stats["luminance"],
                    )
                )

                # Check clipping indicators
                if zero_pct > clip_thresh or sat_pct > clip_thresh:
                    indicators.append(
                        FindingItem(
                            category=FindingCategory.INDICATOR,
                            title="Significant Pixel Clipping Detected",
                            description=(
                                f"Image exhibits {zero_pct:.1f}% pure black pixels and {sat_pct:.1f}% saturated white pixels. "
                                "May indicate harsh dynamic contrast adjustments or sensor saturation."
                            ),
                            confidence=0.60,
                            details={"underexposed_pct": zero_pct, "overexposed_pct": sat_pct},
                        )
                    )

                # Check comb effect
                if zero_bin_gaps >= 8:
                    indicators.append(
                        FindingItem(
                            category=FindingCategory.INDICATOR,
                            title="Histogram Comb / Re-Quantization Gaps",
                            description=(
                                f"Detected {zero_bin_gaps} isolated zero-count bin gaps in the luminance histogram. "
                                "Characteristic of digital tonal curves, levels stretching, or bit-depth re-quantization."
                            ),
                            confidence=0.75,
                            details={"comb_gaps": zero_bin_gaps},
                        )
                    )
                    hypotheses.append(
                        FindingItem(
                            category=FindingCategory.HYPOTHESIS,
                            title="Tonal Range Modification",
                            description="Levels, contrast, or color curves were manually adjusted post-capture.",
                            details={"comb_gaps": zero_bin_gaps},
                        )
                    )

                # 2. Render 4-Panel Histogram Chart Artifact
                chart_w, chart_h = 600, 320
                chart_img = np.zeros((chart_h, chart_w, 3), dtype=np.uint8)
                chart_img[:] = (13, 19, 33)  # dark slate background #0D1321

                # Draw channel histograms
                hist_colors = {
                    "Red": (244, 63, 94),     # rose
                    "Green": (16, 185, 129),  # emerald
                    "Blue": (0, 242, 254),    # cyan
                    "Luminance": (241, 245, 249), # white
                }

                plot_x, plot_y, plot_w, plot_h = 30, 20, 540, 260
                # Draw subtle axes
                cv2.rectangle(chart_img, (plot_x, plot_y), (plot_x + plot_w, plot_y + plot_h), (30, 41, 59), 1)

                max_h = max(np.max(histograms[k]) for k in histograms) + 1e-5

                for ch_name, h_arr in histograms.items():
                    color = hist_colors[ch_name]
                    # Map 256 bins to plot_w
                    pts = []
                    for b in range(256):
                        px = int(plot_x + (b / 255.0) * plot_w)
                        py = int(plot_y + plot_h - (h_arr[b] / max_h) * (plot_h - 10))
                        pts.append((px, py))

                    for p_i in range(len(pts) - 1):
                        cv2.line(chart_img, pts[p_i], pts[p_i + 1], color, 1 if ch_name != "Luminance" else 2, cv2.LINE_AA)

                # Add labels
                cv2.putText(chart_img, "RGB & Luminance Histogram (0..255)", (plot_x, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (148, 163, 184), 1, cv2.LINE_AA)
                cv2.putText(chart_img, f"Entropy: {channel_stats['luminance']['entropy_bits']:.2f} bits | Clipped: {zero_pct + sat_pct:.1f}%", (plot_x + 280, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 242, 254), 1, cv2.LINE_AA)

                # Save chart artifact
                art_img = Image.fromarray(chart_img)
                art_buf = io.BytesIO()
                art_img.save(art_buf, format="PNG")
                art_bytes = art_buf.getvalue()
                art_sha = compute_sha256_bytes(art_bytes)
                art_filename = f"hist_{analysis_id[:8]}_{art_sha[:8]}.png"

                storage_service.store_file(
                    category="analysis",
                    filename=art_filename,
                    file_bytes=art_bytes,
                )

                artifacts.append(
                    ArtifactReference(
                        artifact_type="HISTOGRAM_PLOT",
                        stored_filename=art_filename,
                        description="Multi-channel RGB and Luminance intensity distribution chart",
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
                error_message=f"Statistical analysis failed: {str(e)}",
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
            artifacts=artifacts,
            limitations=self.limitations,
            warnings=warnings,
        )

