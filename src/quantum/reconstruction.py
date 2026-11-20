"""
Measurement decoding, difference-map reconstruction, and Coupon Collector analysis.
"""
import math
from typing import Dict, List, Tuple, Optional
import numpy as np

from src.quantum.types import PixelSample, ReconstructionResult


def decode_16q_bitstring(bitstring: str) -> Tuple[int, int, int, int]:
    """
    Decodes a 16-qubit measurement bitstring into (pos_index, orig_val, mod_val, diff_val).
    
    Qiskit space-separated format: '<m_diff> <m_mod> <m_orig> <m_pos>'
    If contiguous string without spaces (16 chars):
    indices: diff (0..3), mod (4..7), orig (8..11), pos (12..15)
    """
    cleaned = bitstring.strip()
    if " " in cleaned:
        parts = cleaned.split(" ")
        if len(parts) != 4:
            raise ValueError(f"Expected 4 space-separated registers, got {len(parts)} in '{bitstring}'")
        diff_str, mod_str, orig_str, pos_str = parts[0], parts[1], parts[2], parts[3]
    else:
        if len(cleaned) != 16:
            raise ValueError(f"Expected 16-character bitstring, got {len(cleaned)} in '{bitstring}'")
        diff_str = cleaned[0:4]
        mod_str = cleaned[4:8]
        orig_str = cleaned[8:12]
        pos_str = cleaned[12:16]

    return int(pos_str, 2), int(orig_str, 2), int(mod_str, 2), int(diff_str, 2)


def decode_12q_bitstring(bitstring: str) -> Tuple[int, int, Optional[int], int]:
    """
    Decodes a 12-qubit measurement bitstring into (pos_index, orig_val, None, diff_val).
    
    Qiskit space-separated format: '<m_diff> <m_orig> <m_pos>'
    """
    cleaned = bitstring.strip()
    if " " in cleaned:
        parts = cleaned.split(" ")
        if len(parts) != 3:
            raise ValueError(f"Expected 3 space-separated registers, got {len(parts)} in '{bitstring}'")
        diff_str, orig_str, pos_str = parts[0], parts[1], parts[2]
    else:
        if len(cleaned) != 12:
            raise ValueError(f"Expected 12-character bitstring, got {len(cleaned)} in '{bitstring}'")
        diff_str = cleaned[0:4]
        orig_str = cleaned[4:8]
        pos_str = cleaned[8:12]

    return int(pos_str, 2), int(orig_str, 2), None, int(diff_str, 2)


def reconstruct_from_counts(
    counts: Dict[str, int],
    architecture: str = "16-qubit",
    total_shots: Optional[int] = None,
) -> ReconstructionResult:
    """
    Aggregates measurement shot counts into 4x4 spatial difference maps.
    
    Unobserved coordinates are explicitly assigned -1 and included in missing_coordinates.
    An unobserved coordinate is NEVER falsely reported as unchanged (0).
    """
    # -1 indicates unobserved
    recon_orig = np.full((4, 4), -1, dtype=int)
    recon_mod = np.full((4, 4), -1, dtype=int)
    recon_diff = np.full((4, 4), -1, dtype=int)
    sampled_counts_map = np.zeros((4, 4), dtype=int)
    pixel_samples: Dict[Tuple[int, int], PixelSample] = {}

    computed_total_shots = sum(counts.values())
    shots = total_shots if total_shots is not None else computed_total_shots

    decoder = decode_16q_bitstring if "16" in architecture else decode_12q_bitstring

    for bitstring, count in counts.items():
        pos_idx, orig_val, mod_val, diff_val = decoder(bitstring)
        if not (0 <= pos_idx < 16):
            continue

        r = pos_idx // 4
        c = pos_idx % 4

        sampled_counts_map[r, c] += count
        recon_orig[r, c] = orig_val
        recon_diff[r, c] = diff_val
        if mod_val is not None:
            recon_mod[r, c] = mod_val

    missing_coords: List[Tuple[int, int]] = []
    observed_count = 0

    for r in range(4):
        for c in range(4):
            count = int(sampled_counts_map[r, c])
            k = 4 * r + c
            if count > 0:
                observed_count += 1
                diff_val = int(recon_diff[r, c])
                pixel_samples[(r, c)] = PixelSample(
                    row=r,
                    col=c,
                    coordinate_index=k,
                    observed_count=count,
                    orig_intensity=int(recon_orig[r, c]),
                    mod_intensity=int(recon_mod[r, c]) if recon_mod[r, c] != -1 else None,
                    diff_intensity=diff_val,
                    is_observed=True,
                    is_tampered=diff_val > 0,
                )
            else:
                missing_coords.append((r, c))
                pixel_samples[(r, c)] = PixelSample(
                    row=r,
                    col=c,
                    coordinate_index=k,
                    observed_count=0,
                    orig_intensity=None,
                    mod_intensity=None,
                    diff_intensity=None,
                    is_observed=False,
                    is_tampered=False,
                )

    return ReconstructionResult(
        reconstructed_orig=recon_orig,
        reconstructed_mod=recon_mod,
        reconstructed_diff=recon_diff,
        sampled_counts_map=sampled_counts_map,
        total_shots=shots,
        observed_coordinates_count=observed_count,
        missing_coordinates=missing_coords,
        is_fully_reconstructed=observed_count == 16,
        pixel_samples=pixel_samples,
    )


def coupon_collector_expected_shots(n: int = 16) -> float:
    r"""
    Computes exact expected shots to observe all N equiprobable states:
    E[T] = N * \sum_{i=1}^N (1 / i) = N * H_N
    """
    hn = sum(1.0 / i for i in range(1, n + 1))
    return n * hn


def coupon_collector_exact_probability(n: int, s: int) -> float:
    r"""
    Computes exact probability of observing all N states after S independent shots
    using the analytic inclusion-exclusion formula:
    P(all N collected) = \sum_{j=0}^N (-1)^j \binom{N}{j} ((N - j) / N)^S
    """
    if s < n:
        return 0.0
    total = 0.0
    for j in range(n + 1):
        sign = (-1) ** j
        comb = math.comb(n, j)
        term = sign * comb * (((n - j) / n) ** s)
        total += term
    return max(0.0, min(1.0, total))


def coupon_collector_poisson_approx(n: int, s: int) -> float:
    r"""
    Computes the Poisson tail approximation:
    P \approx \exp(-N * \exp(-S / N))
    """
    try:
        val = math.exp(-n * math.exp(-s / n))
        return max(0.0, min(1.0, val))
    except OverflowError:
        return 1.0

