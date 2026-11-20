"""
Classical comparator module for Q-TRACE.
Provides deterministic ground-truth comparison for 4x4 4-bit grayscale images.
"""
from typing import Dict, Any, Tuple
import numpy as np


def validate_4x4_4bit_image(image: np.ndarray, name: str = "image") -> None:
    """
    Validates that the input is a 4x4 2D numpy array with integer intensities in [0, 15].
    
    Raises:
        ValueError: If shape, dimensionality, or intensity values are out of bounds.
        TypeError: If input is not a numpy array or compatible array.
    """
    if not isinstance(image, np.ndarray):
        raise TypeError(f"{name} must be a numpy ndarray, got {type(image)}")
    
    if image.shape != (4, 4):
        raise ValueError(f"{name} must have shape (4, 4), got {image.shape}")
    
    if not np.issubdtype(image.dtype, np.integer):
        raise TypeError(f"{name} must contain integers, got {image.dtype}")
    
    if np.any(image < 0) or np.any(image > 15):
        min_val, max_val = int(np.min(image)), int(np.max(image))
        raise ValueError(
            f"{name} intensities must be 4-bit integers in [0, 15]. Got min={min_val}, max={max_val}"
        )


def classical_xor_difference(img_a: np.ndarray, img_b: np.ndarray) -> np.ndarray:
    """
    Computes exact bitwise XOR difference between two 4x4 4-bit images.
    
    D(y, x) = A(y, x) ^ B(y, x)
    """
    validate_4x4_4bit_image(img_a, "img_a")
    validate_4x4_4bit_image(img_b, "img_b")
    return np.bitwise_xor(img_a, img_b).astype(np.uint8)


def classical_abs_difference(img_a: np.ndarray, img_b: np.ndarray) -> np.ndarray:
    """
    Computes absolute intensity difference between two 4x4 images.
    
    D_abs(y, x) = |A(y, x) - B(y, x)|
    """
    validate_4x4_4bit_image(img_a, "img_a")
    validate_4x4_4bit_image(img_b, "img_b")
    return np.abs(img_a.astype(int) - img_b.astype(int)).astype(np.uint8)


def classical_threshold_mask(diff: np.ndarray, threshold: int = 0) -> np.ndarray:
    """
    Generates a binary change mask where diff > threshold.
    """
    return (diff > threshold).astype(np.uint8)


def calculate_difference_metrics(img_a: np.ndarray, img_b: np.ndarray) -> Dict[str, Any]:
    """
    Calculates comprehensive classical difference metrics for a pair of images.
    
    Returns:
        Dictionary containing:
        - changed_pixels_count: Total coordinates where A != B
        - max_xor_difference: Highest bitwise XOR value observed
        - max_abs_difference: Highest absolute delta observed
        - mean_abs_difference: Average absolute delta
        - xor_map: 4x4 XOR difference array
        - abs_map: 4x4 Absolute difference array
        - is_identical: Boolean flag
    """
    validate_4x4_4bit_image(img_a, "img_a")
    validate_4x4_4bit_image(img_b, "img_b")
    
    xor_map = classical_xor_difference(img_a, img_b)
    abs_map = classical_abs_difference(img_a, img_b)
    changed_mask = xor_map > 0
    changed_count = int(np.sum(changed_mask))
    
    return {
        "changed_pixels_count": changed_count,
        "total_pixels": 16,
        "is_identical": changed_count == 0,
        "max_xor_difference": int(np.max(xor_map)),
        "max_abs_difference": int(np.max(abs_map)),
        "mean_abs_difference": float(np.mean(abs_map)),
        "xor_map": xor_map,
        "abs_map": abs_map,
    }

