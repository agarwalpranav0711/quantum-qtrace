"""
Classical image forensics and comparison baseline modules.
"""
from src.classical.comparator import (
    classical_xor_difference,
    classical_abs_difference,
    classical_threshold_mask,
    calculate_difference_metrics,
    validate_4x4_4bit_image,
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

