"""
Tests for measurement bitstring decoding, difference-map reconstruction, and Coupon Collector math.
"""
import numpy as np
import pytest

from src.quantum.reconstruction import (
    decode_16q_bitstring,
    decode_12q_bitstring,
    reconstruct_from_counts,
    coupon_collector_expected_shots,
    coupon_collector_exact_probability,
    coupon_collector_poisson_approx,
)


def test_decode_16q_space_separated():
    # Format: '<diff> <mod> <orig> <pos>'
    # diff=11 (1011), mod=12 (1100), orig=7 (0111), pos=6 (0110)
    bstr = "1011 1100 0111 0110"
    pos, orig, mod, diff = decode_16q_bitstring(bstr)
    assert pos == 6
    assert orig == 7
    assert mod == 12
    assert diff == 11


def test_decode_16q_contiguous():
    # Contiguous: diff(4) mod(4) orig(4) pos(4)
    bstr = "1011110001110110"
    pos, orig, mod, diff = decode_16q_bitstring(bstr)
    assert pos == 6
    assert orig == 7
    assert mod == 12
    assert diff == 11


def test_decode_12q_space_separated():
    # Format: '<diff> <orig> <pos>'
    bstr = "1011 0111 0110"
    pos, orig, mod, diff = decode_12q_bitstring(bstr)
    assert pos == 6
    assert orig == 7
    assert mod is None
    assert diff == 11


def test_unobserved_pixels_never_classified_as_zero():
    """
    Critical requirement: If a coordinate is not observed during sampling,
    it must NOT be marked as 0 (unchanged). It must be marked as -1 (unobserved)
    and included in missing_coordinates.
    """
    # Create artificial counts missing coordinate k=5 (row 1, col 1)
    fake_counts = {}
    for k in range(16):
        if k == 5:
            continue  # Coordinate 5 is missing
        pos_s = f"{k:04b}"
        bstr = f"0000 0001 0001 {pos_s}"
        fake_counts[bstr] = 10

    recon = reconstruct_from_counts(fake_counts, architecture="16-qubit")
    assert not recon.is_fully_reconstructed
    assert (1, 1) in recon.missing_coordinates
    assert len(recon.missing_coordinates) == 1
    assert recon.reconstructed_diff[1, 1] == -1  # Must be -1, NOT 0
    assert recon.sampled_counts_map[1, 1] == 0
    assert recon.pixel_samples[(1, 1)].is_observed is False


def test_coupon_collector_expected_value():
    e_t = coupon_collector_expected_shots(16)
    # E[T] = 16 * H_16 ≈ 54.09166
    assert np.isclose(e_t, 54.09166, atol=1e-3)


def test_coupon_collector_exact_probability():
    # S < 16 must have 0 probability
    assert coupon_collector_exact_probability(16, 10) == 0.0

    p_54 = coupon_collector_exact_probability(16, 54)
    assert 0.58 <= p_54 <= 0.60  # ≈ 0.59097

    p_100 = coupon_collector_exact_probability(16, 100)
    assert 0.97 <= p_100 <= 0.98  # ≈ 0.97500

    p_150 = coupon_collector_exact_probability(16, 150)
    assert p_150 >= 0.999  # Exact 99.9% threshold

    p_1024 = coupon_collector_exact_probability(16, 1024)
    assert np.isclose(p_1024, 1.0, atol=1e-12)


def test_coupon_collector_poisson_approx():
    approx_155 = coupon_collector_poisson_approx(16, 155)
    assert approx_155 >= 0.999

