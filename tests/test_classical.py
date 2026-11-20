"""
Tests for classical image comparison and test dataset generation.
"""
import pytest
import numpy as np

from src.classical.comparator import (
    validate_4x4_4bit_image,
    classical_xor_difference,
    classical_abs_difference,
    classical_threshold_mask,
    calculate_difference_metrics,
)
from src.classical.test_data import (
    get_standard_test_cases,
    create_test_case_identical,
    create_test_case_single_pixel,
    create_test_case_multi_pixel,
    create_test_case_full_change,
    create_test_case_boundary,
    create_test_case_max_difference,
    create_test_case_zero_difference,
    create_test_case_random,
)


def test_image_validation_valid():
    valid = np.arange(16, dtype=np.uint8).reshape((4, 4))
    validate_4x4_4bit_image(valid)  # Should not raise


def test_image_validation_invalid_shape():
    invalid_shape = np.zeros((3, 3), dtype=np.uint8)
    with pytest.raises(ValueError, match="must have shape"):
        validate_4x4_4bit_image(invalid_shape)


def test_image_validation_invalid_range():
    out_of_bounds = np.full((4, 4), 16, dtype=np.uint8)
    with pytest.raises(ValueError, match="intensities must be 4-bit integers"):
        validate_4x4_4bit_image(out_of_bounds)

    negative = np.full((4, 4), -1, dtype=int)
    with pytest.raises(ValueError, match="intensities must be 4-bit integers"):
        validate_4x4_4bit_image(negative)


def test_classical_xor_logic():
    a = np.array([[7, 0, 15, 8],
                  [1, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9, 10, 11, 12]], dtype=np.uint8)
    b = np.array([[12, 0, 0, 8],
                  [1, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9, 10, 11, 12]], dtype=np.uint8)
    diff = classical_xor_difference(a, b)
    assert diff[0, 0] == 7 ^ 12  # 11
    assert diff[0, 1] == 0
    assert diff[0, 2] == 15
    assert diff[0, 3] == 0
    assert np.all(diff[1:, :] == 0)


def test_classical_abs_difference():
    a = np.array([[10, 5, 2, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]], dtype=np.uint8)
    b = np.array([[3, 5, 8, 15],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]], dtype=np.uint8)
    diff_abs = classical_abs_difference(a, b)
    assert diff_abs[0, 0] == 7
    assert diff_abs[0, 1] == 0
    assert diff_abs[0, 2] == 6
    assert diff_abs[0, 3] == 15


def test_difference_metrics_calculation():
    tc = create_test_case_single_pixel()
    metrics = calculate_difference_metrics(tc["img_a"], tc["img_b"])
    assert metrics["changed_pixels_count"] == 1
    assert metrics["is_identical"] is False
    assert metrics["max_xor_difference"] == 11
    assert metrics["max_abs_difference"] == 5


def test_standard_test_cases_structure():
    cases = get_standard_test_cases()
    assert len(cases) == 8
    for c in cases:
        validate_4x4_4bit_image(c["img_a"])
        validate_4x4_4bit_image(c["img_b"])
        assert "case_id" in c
        assert "expected_changed_count" in c
        assert len(c["expected_changed_coords"]) == c["expected_changed_count"]

