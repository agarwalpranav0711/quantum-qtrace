"""Integration adapter bridging FastAPI requests with the Part 2 Quantum Image Engine."""

import time
from typing import List, Literal, Optional, Dict, Any
import numpy as np

from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import reconstruct_from_counts
from src.classical.comparator import classical_xor_difference
from backend.app.core.exceptions import QuantumProcessingException
from backend.app.core.logging import get_logger

logger = get_logger("quantum_adapter")


class QuantumAdapter:
    """Service adapter executing quantum comparison circuits and returning structured metrics."""

    def run_comparison(
        self,
        patch_a: List[List[int]],
        patch_b: List[List[int]],
        architecture: Literal["16q", "12q"] = "16q",
        shots: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute quantum patch comparison using either 16-qubit or 12-qubit architecture.

        Args:
            patch_a: 4x4 list of pixel intensities (0-15 or 0-255).
            patch_b: 4x4 list of pixel intensities (0-15 or 0-255).
            architecture: '16q' or '12q'.
            shots: Measurement shot count (defaults to coupon collector recommendation: 1024).

        Returns:
            Dictionary formatted to match QuantumComparisonResponse schema.
        """
        start_time = time.perf_counter()
        shots_to_use = shots if (shots is not None and shots > 0) else 1024

        try:
            arr_a = np.array(patch_a, dtype=np.uint8)
            arr_b = np.array(patch_b, dtype=np.uint8)

            # If inputs are 8-bit (max > 15), quantize down to 4-bit range [0, 15] for the 4-qubit color register
            if np.max(arr_a) > 15:
                arr_a = (arr_a >> 4).astype(np.uint8)
            if np.max(arr_b) > 15:
                arr_b = (arr_b >> 4).astype(np.uint8)

            # 1. Instantiate the circuit builder
            if architecture == "16q":
                comparator = QuantumComparator16Q(arr_a, arr_b)
                counts, resources = comparator.run_simulation(shots=shots_to_use, seed_simulator=42)
                recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=shots_to_use)
            elif architecture == "12q":
                comparator = QuantumComparator12Q(arr_a, arr_b)
                counts, resources = comparator.run_simulation(shots=shots_to_use, seed_simulator=42)
                recon = reconstruct_from_counts(counts, architecture="12-qubit", total_shots=shots_to_use)
            else:
                raise QuantumProcessingException(f"Unsupported quantum architecture: '{architecture}'.")

            # 2. Compute classical difference map as ground truth
            classical_diff = classical_xor_difference(arr_a, arr_b)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # Count differences on observed coordinates
            observed_diff = recon.reconstructed_diff
            # Replace unobserved (-1) with 0 for clean output map representation
            clean_diff_map = np.where(observed_diff >= 0, observed_diff, 0)
            diff_count = int(np.count_nonzero(clean_diff_map))
            coverage_ratio = float(recon.observed_coordinates_count / 16.0)

            # Fidelity against classical ground truth
            if recon.observed_coordinates_count > 0:
                mask = observed_diff >= 0
                fidelity = float(np.mean(clean_diff_map[mask] == classical_diff[mask]))
            else:
                fidelity = 0.0

            is_identical = bool(diff_count == 0 and coverage_ratio >= 0.99)

            result = {
                "architecture": architecture,
                "qubits": resources.num_qubits,
                "depth": resources.circuit_depth,
                "gate_count": resources.total_gate_count,
                "fidelity": round(fidelity, 4),
                "reconstructed_diff_map": clean_diff_map.tolist(),
                "classical_diff_map": classical_diff.tolist(),
                "difference_count": diff_count,
                "coverage_ratio": round(coverage_ratio, 4),
                "shots_used": shots_to_use,
                "execution_time_ms": round(elapsed_ms, 2),
                "identical": is_identical,
            }

            logger.info(
                f"Quantum comparison ({architecture}) completed in {elapsed_ms:.1f}ms: "
                f"fidelity={fidelity:.4f}, diff_pixels={diff_count}, coverage={coverage_ratio:.2%}"
            )
            return result

        except QuantumProcessingException:
            raise
        except Exception as e:
            logger.error(f"Quantum comparison failed: {str(e)}")
            raise QuantumProcessingException(f"Quantum comparison error: {str(e)}")


_quantum_adapter: Optional[QuantumAdapter] = None


def get_quantum_adapter() -> QuantumAdapter:
    """Return singleton instance of QuantumAdapter."""
    global _quantum_adapter
    if _quantum_adapter is None:
        _quantum_adapter = QuantumAdapter()
    return _quantum_adapter
