"""
End-to-end integration tests for Q-TRACE Part 2.
Validates complete equivalence between classical and quantum image comparison across test suites.
"""
import numpy as np
import pytest

from src.classical.test_data import get_standard_test_cases, create_test_case_random
from src.classical.comparator import classical_xor_difference
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import reconstruct_from_counts
from src.quantum.resource_estimator import calculate_raw_statevector_memory


@pytest.mark.parametrize("tc", get_standard_test_cases(), ids=lambda c: c["case_id"])
def test_end_to_end_standard_cases_16q(tc):
    img_a = tc["img_a"]
    img_b = tc["img_b"]
    expected_diff = classical_xor_difference(img_a, img_b)

    comp = QuantumComparator16Q(img_a, img_b)
    counts, res = comp.run_simulation(shots=1024, seed_simulator=42)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    assert recon.is_fully_reconstructed, f"Incomplete reconstruction for {tc['case_id']}"
    assert np.array_equal(recon.reconstructed_diff, expected_diff), f"Diff mismatch for {tc['case_id']}"
    assert np.array_equal(recon.reconstructed_orig, img_a), f"Orig mismatch for {tc['case_id']}"
    assert np.array_equal(recon.reconstructed_mod, img_b), f"Mod mismatch for {tc['case_id']}"


@pytest.mark.parametrize("tc", get_standard_test_cases(), ids=lambda c: c["case_id"])
def test_end_to_end_standard_cases_12q(tc):
    img_a = tc["img_a"]
    img_b = tc["img_b"]
    expected_diff = classical_xor_difference(img_a, img_b)

    comp = QuantumComparator12Q(img_a, img_b)
    counts, res = comp.run_simulation(shots=1024, seed_simulator=42)
    recon = reconstruct_from_counts(counts, architecture="12-qubit", total_shots=1024)

    assert recon.is_fully_reconstructed, f"Incomplete reconstruction for {tc['case_id']}"
    assert np.array_equal(recon.reconstructed_diff, expected_diff), f"Diff mismatch for {tc['case_id']}"


@pytest.mark.parametrize("seed", [101, 202, 303, 404, 505])
def test_end_to_end_random_trials(seed):
    tc = create_test_case_random(seed=seed)
    img_a, img_b = tc["img_a"], tc["img_b"]
    expected_diff = classical_xor_difference(img_a, img_b)

    comp_16 = QuantumComparator16Q(img_a, img_b)
    counts, _ = comp_16.run_simulation(shots=1024, seed_simulator=seed)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    assert recon.is_fully_reconstructed
    assert np.array_equal(recon.reconstructed_diff, expected_diff)


def test_memory_scaling_calculations():
    mem_16 = calculate_raw_statevector_memory(16)
    assert mem_16["num_amplitudes"] == 65536
    assert mem_16["total_bytes"] == 1048576  # Exact 1.0 MiB
    assert mem_16["is_simulatable_on_laptop"] is True

    mem_12 = calculate_raw_statevector_memory(12)
    assert mem_12["num_amplitudes"] == 4096
    assert mem_12["total_bytes"] == 65536  # Exact 64 KiB
    assert mem_12["is_simulatable_on_laptop"] is True

    mem_42 = calculate_raw_statevector_memory(42)
    assert "64.00 TiB" in mem_42["formatted_binary"]
    assert mem_42["is_simulatable_on_laptop"] is False

    mem_48 = calculate_raw_statevector_memory(48)
    assert "4.00 PiB" in mem_48["formatted_binary"]
    assert mem_48["is_simulatable_on_laptop"] is False

