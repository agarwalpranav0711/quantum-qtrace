"""
Test data generator module for Q-TRACE Part 2.
Provides deterministic, reproducible 4x4 4-bit grayscale test image pairs.
"""
from typing import Dict, Any, List
import numpy as np


def create_base_image_gradient() -> np.ndarray:
    """
    Standard sequential gradient image defined in directive:
    [[ 1,  2,  3,  4],
     [ 5,  6,  7,  8],
     [ 9, 10, 11, 12],
     [13, 14, 15,  0]]
    """
    return np.array([
        [1,  2,  3,  4],
        [5,  6,  7,  8],
        [9, 10, 11, 12],
        [13, 14, 15, 0]
    ], dtype=np.uint8)


def create_test_case_identical() -> Dict[str, Any]:
    """Test Case 1: Identical images (0 differences)."""
    img_a = create_base_image_gradient()
    img_b = img_a.copy()
    return {
        "case_id": "TC-01-IDENTICAL",
        "description": "Identical gradient image pair (zero differences)",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 0,
        "expected_changed_coords": [],
    }


def create_test_case_single_pixel() -> Dict[str, Any]:
    """
    Test Case 2: Single-pixel change.
    Row 1, Column 2 changes from 7 to 12 (7 ^ 12 = 11).
    """
    img_a = create_base_image_gradient()
    img_b = img_a.copy()
    img_b[1, 2] = 12
    return {
        "case_id": "TC-02-SINGLE-PIXEL",
        "description": "Single-pixel change at (row 1, col 2) from 7 to 12 (XOR=11)",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 1,
        "expected_changed_coords": [(1, 2)],
    }


def create_test_case_multi_pixel() -> Dict[str, Any]:
    """Test Case 3: Multiple sparse pixel changes (4 coordinates changed)."""
    img_a = create_base_image_gradient()
    img_b = img_a.copy()
    # Modify 4 distinct coordinates
    img_b[0, 1] = 10  # 2 -> 10 (2 ^ 10 = 8)
    img_b[1, 3] = 0   # 8 -> 0  (8 ^ 0 = 8)
    img_b[2, 0] = 5   # 9 -> 5  (9 ^ 5 = 12)
    img_b[3, 2] = 2   # 15 -> 2 (15 ^ 2 = 13)
    return {
        "case_id": "TC-03-MULTI-PIXEL",
        "description": "Four sparse pixel changes across quadrants",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 4,
        "expected_changed_coords": [(0, 1), (1, 3), (2, 0), (3, 2)],
    }


def create_test_case_full_change() -> Dict[str, Any]:
    """Test Case 4: Every pixel changed (16 differences)."""
    img_a = create_base_image_gradient()
    # Invert all bits (bitwise NOT restricted to 4 bits: 15 - val)
    img_b = (15 - img_a).astype(np.uint8)
    coords = [(r, c) for r in range(4) for c in range(4)]
    return {
        "case_id": "TC-04-FULL-CHANGE",
        "description": "Every pixel modified via 4-bit inversion (16 differences)",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 16,
        "expected_changed_coords": coords,
    }


def create_test_case_boundary() -> Dict[str, Any]:
    """Test Case 5: Boundary corners and perimeter modifications."""
    img_a = create_base_image_gradient()
    img_b = img_a.copy()
    # Modify the 4 corners
    img_b[0, 0] = 14  # (0, 0)
    img_b[0, 3] = 1   # (0, 3)
    img_b[3, 0] = 2   # (3, 0)
    img_b[3, 3] = 15  # (3, 3)
    return {
        "case_id": "TC-05-BOUNDARY-CORNERS",
        "description": "Modifications restricted strictly to the 4 corners",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 4,
        "expected_changed_coords": [(0, 0), (0, 3), (3, 0), (3, 3)],
    }


def create_test_case_max_difference() -> Dict[str, Any]:
    """Test Case 6: Maximum intensity differences (0 vs 15, XOR=15)."""
    img_a = np.zeros((4, 4), dtype=np.uint8)
    img_b = np.full((4, 4), 15, dtype=np.uint8)
    coords = [(r, c) for r in range(4) for c in range(4)]
    return {
        "case_id": "TC-06-MAX-DIFFERENCE",
        "description": "All-zero image vs All-fifteen image (Maximum XOR=15)",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 16,
        "expected_changed_coords": coords,
    }


def create_test_case_zero_difference() -> Dict[str, Any]:
    """Test Case 7: All zeros pair."""
    img_a = np.zeros((4, 4), dtype=np.uint8)
    img_b = np.zeros((4, 4), dtype=np.uint8)
    return {
        "case_id": "TC-07-ZERO-IMAGE-PAIR",
        "description": "All-zero image compared against all-zero image",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": 0,
        "expected_changed_coords": [],
    }


def create_test_case_random(seed: int = 42) -> Dict[str, Any]:
    """Test Case 8: Reproducible random image pair with fixed seed."""
    rng = np.random.default_rng(seed)
    img_a = rng.integers(0, 16, size=(4, 4), dtype=np.uint8)
    img_b = img_a.copy()
    # Randomly modify 3 distinct coordinates
    chosen_indices = rng.choice(16, size=3, replace=False)
    for idx in chosen_indices:
        r, c = idx // 4, idx % 4
        # Pick a different value in [0, 15]
        new_val = (img_a[r, c] + rng.integers(1, 16)) % 16
        img_b[r, c] = new_val
    
    diff_mask = img_a != img_b
    changed_coords = [(int(r), int(c)) for r, c in zip(*np.where(diff_mask))]
    
    return {
        "case_id": f"TC-08-RANDOM-SEED-{seed}",
        "description": f"Reproducible random image pair generated with seed {seed}",
        "img_a": img_a,
        "img_b": img_b,
        "expected_changed_count": len(changed_coords),
        "expected_changed_coords": changed_coords,
    }


def get_standard_test_cases() -> List[Dict[str, Any]]:
    """Returns a list of all 8 standard test cases for systematic benchmarking."""
    return [
        create_test_case_identical(),
        create_test_case_single_pixel(),
        create_test_case_multi_pixel(),
        create_test_case_full_change(),
        create_test_case_boundary(),
        create_test_case_max_difference(),
        create_test_case_zero_difference(),
        create_test_case_random(seed=42),
    ]

