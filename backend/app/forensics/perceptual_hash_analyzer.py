"""Perceptual Hashing and Visual Similarity forensic analyzer."""

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
)
from backend.app.storage.service import StorageService
from backend.app.services.integrity import compute_sha256_bytes


def compute_ahash(gray_img: np.ndarray) -> str:
    """Compute 64-bit Average Hash (aHash)."""
    resized = cv2.resize(gray_img, (8, 8), interpolation=cv2.INTER_AREA)
    avg = np.mean(resized)
    bits = (resized > avg).flatten()
    val = 0
    for b in bits:
        val = (val << 1) | int(b)
    return f"{val:016x}"


def compute_dhash(gray_img: np.ndarray) -> str:
    """Compute 64-bit Difference Hash (dHash)."""
    resized = cv2.resize(gray_img, (9, 8), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    bits = diff.flatten()
    val = 0
    for b in bits:
        val = (val << 1) | int(b)
    return f"{val:016x}"


def compute_phash(gray_img: np.ndarray) -> str:
    """Compute 64-bit DCT-based Perceptual Hash (pHash)."""
    resized = cv2.resize(gray_img, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    dct = cv2.dct(resized)
    # Extract top-left 8x8 low-frequency coefficients, excluding DC component (0,0)
    dct_low = dct[0:8, 0:8]
    med = np.median(dct_low[1:, 1:])
    bits = (dct_low > med).flatten()
    val = 0
    for b in bits:
        val = (val << 1) | int(b)
    return f"{val:016x}"


def hamming_distance(hex1: str, hex2: str) -> int:
    """Compute bitwise Hamming distance between two 64-bit hex strings."""
    v1 = int(hex1, 16)
    v2 = int(hex2, 16)
    return bin(v1 ^ v2).count("1")


class PerceptualHashAnalyzer(ForensicTechnique):
    """Computes perceptual image fingerprints (aHash, dHash, pHash) for visual similarity matching."""

    id: str = "perceptual_hash"
    name: str = "Perceptual Hashing & Similarity Fingerprinting"
    version: str = "1.0.0"
    category: str = "Fingerprinting & Identity"
    description: (
        "Calculates 64-bit visual perceptual hashes (aHash, dHash, DCT-based pHash) invariant "
        "to compression and minor scaling. Distinguishes bitstream identity from visual similarity."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {
        "reference_phash": None,  # Optional hex string for comparative similarity testing
    }
    limitations: List[str] = [
        "Perceptual hashes are designed to tolerate minor scaling and compression; they do NOT detect localized splices.",
        "Major cropping, rotation, or extensive occlusions significantly alter perceptual hashes.",
        "Perceptual similarity (Hamming distance) must NEVER be confused with cryptographic SHA-256 bitstream identity.",
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
        ref_phash = params.get("reference_phash")

        observations: List[FindingItem] = []
        indicators: List[FindingItem] = []
        hypotheses: List[FindingItem] = []
        metrics: Dict[str, Any] = {}
        warnings: List[str] = []

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                gray_arr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY)

                # Compute hashes
                ahash_val = compute_ahash(gray_arr)
                dhash_val = compute_dhash(gray_arr)
                phash_val = compute_phash(gray_arr)
                sha256_val = compute_sha256_bytes(image_bytes)

                metrics["ahash"] = ahash_val
                metrics["dhash"] = dhash_val
                metrics["phash"] = phash_val
                metrics["sha256_bitstream"] = sha256_val

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Perceptual Hashes Computed",
                        description=(
                            f"DCT pHash: {phash_val}, dHash: {dhash_val}, aHash: {ahash_val}. "
                            f"Cryptographic SHA-256: {sha256_val[:16]}..."
                        ),
                        details={
                            "phash": phash_val,
                            "dhash": dhash_val,
                            "ahash": ahash_val,
                            "sha256": sha256_val,
                        },
                    )
                )

                # Compare against reference hash if provided
                if ref_phash and isinstance(ref_phash, str) and len(ref_phash) == 16:
                    dist = hamming_distance(phash_val, ref_phash)
                    sim_pct = (1.0 - (dist / 64.0)) * 100.0
                    metrics["reference_comparison"] = {
                        "reference_phash": ref_phash,
                        "hamming_distance": dist,
                        "similarity_percentage": round(sim_pct, 2),
                    }

                    if dist <= 5:
                        observations.append(
                            FindingItem(
                                category=FindingCategory.OBSERVATION,
                                title="Near-Identical Visual Match to Reference",
                                description=f"Hamming distance is {dist}/64 ({sim_pct:.1f}% visual similarity). Images depict the same visual scene.",
                                details={"distance": dist, "similarity": sim_pct},
                            )
                        )
                    elif dist <= 12:
                        observations.append(
                            FindingItem(
                                category=FindingCategory.OBSERVATION,
                                title="Moderate Visual Match to Reference",
                                description=f"Hamming distance is {dist}/64 ({sim_pct:.1f}% similarity). Possible resized, re-compressed, or cropped derivative.",
                                details={"distance": dist, "similarity": sim_pct},
                            )
                        )
                    else:
                        observations.append(
                            FindingItem(
                                category=FindingCategory.OBSERVATION,
                                title="Distinct Visual Scene from Reference",
                                description=f"Hamming distance is {dist}/64 ({sim_pct:.1f}% similarity). Images represent visually distinct scenes.",
                                details={"distance": dist, "similarity": sim_pct},
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
                error_message=f"Perceptual hashing failed: {str(e)}",
                limitations=self.limitations,
            )

        elapsed = (time.perf_counter() - start_time) * 1000.0
        status = ForensicStatus.NO_ANOMALY_DETECTED

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
            limitations=self.limitations,
            warnings=warnings,
        )

