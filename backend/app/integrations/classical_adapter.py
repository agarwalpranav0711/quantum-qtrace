"""Integration adapter for classical image forensic algorithms."""

import time
from typing import List, Dict, Any
import numpy as np

from src.classical.comparator import classical_xor_difference, compute_classical_metrics
from backend.app.core.logging import get_logger

logger = get_logger("classical_adapter")


class ClassicalAdapter:
    """Service adapter for classical pixel comparison and forensic metrics."""

    @staticmethod
    def compare_patches(
        patch_a: List[List[int]],
        patch_b: List[List[int]],
    ) -> Dict[str, Any]:
        """Compare two 4x4 patches using classical bitwise XOR difference."""
        start_time = time.perf_counter()

        arr_a = np.array(patch_a, dtype=np.uint8)
        arr_b = np.array(patch_b, dtype=np.uint8)

        diff = classical_xor_difference(arr_a, arr_b)
        metrics = compute_classical_metrics(arr_a, arr_b, diff)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "algorithm": "CLASSICAL_BITWISE_XOR",
            "diff_map": diff.tolist(),
            "differing_pixels": metrics.differing_pixels,
            "total_pixels": metrics.total_pixels,
            "mean_absolute_difference": float(metrics.mean_absolute_diff),
            "max_absolute_difference": int(metrics.max_absolute_diff),
            "identical": metrics.is_identical,
            "execution_time_ms": round(elapsed_ms, 3),
        }


_classical_adapter = ClassicalAdapter()


def get_classical_adapter() -> ClassicalAdapter:
    """Return ClassicalAdapter instance."""
    return _classical_adapter

