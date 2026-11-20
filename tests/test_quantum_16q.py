"""
Tests for the 16-qubit dedicated difference register NEQR comparison engine.
"""
import numpy as np
import pytest

from src.classical.test_data import (
    create_test_case_identical,
    create_test_case_single_pixel,
    create_test_case_multi_pixel,
    create_test_case_max_difference,
    create_test_case_zero_difference,
)
from src.classical.comparator import classical_xor_difference
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.reconstruction import reconstruct_from_counts


def test_16q_circuit_structure():
    tc = create_test_case_single_pixel()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    qc = comp.build_circuit(with_measurements=True)

    assert qc.num_qubits == 16
    assert qc.num_clbits == 16

    qc_no_meas = comp.build_circuit(with_measurements=False)
    assert qc_no_meas.num_qubits == 16
    assert qc_no_meas.num_clbits == 0


def test_16q_resource_extraction():
    tc = create_test_case_single_pixel()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    res = comp.extract_resources()

    assert res.num_qubits == 16
    assert res.num_clbits == 16
    assert res.two_qubit_gate_count == 8  # 8 CNOT comparison gates
    assert res.raw_statevector_memory_bytes == 2**16 * 16  # 1.05 MB
    assert res.circuit_depth > 0


def test_16q_identical_images():
    tc = create_test_case_identical()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=123)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    assert recon.is_fully_reconstructed
    # For identical images, all difference values must be 0
    assert np.all(recon.reconstructed_diff == 0)
    assert np.array_equal(recon.reconstructed_orig, tc["img_a"])
    assert np.array_equal(recon.reconstructed_mod, tc["img_b"])


def test_16q_single_pixel_change():
    tc = create_test_case_single_pixel()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=456)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    expected_diff = classical_xor_difference(tc["img_a"], tc["img_b"])
    assert np.array_equal(recon.reconstructed_diff, expected_diff)
    # Changed pixel at (1, 2)
    assert recon.reconstructed_diff[1, 2] == 11
    # All other 15 pixels must be 0
    assert np.count_nonzero(recon.reconstructed_diff) == 1


def test_16q_multi_pixel_change():
    tc = create_test_case_multi_pixel()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=789)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    expected_diff = classical_xor_difference(tc["img_a"], tc["img_b"])
    assert np.array_equal(recon.reconstructed_diff, expected_diff)
    assert np.count_nonzero(recon.reconstructed_diff) == 4


def test_16q_max_difference():
    tc = create_test_case_max_difference()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=999)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    assert np.all(recon.reconstructed_diff == 15)
    assert np.all(recon.reconstructed_orig == 0)
    assert np.all(recon.reconstructed_mod == 15)


def test_16q_all_zeros():
    tc = create_test_case_zero_difference()
    comp = QuantumComparator16Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=111)
    recon = reconstruct_from_counts(counts, architecture="16-qubit", total_shots=1024)

    assert np.all(recon.reconstructed_diff == 0)
    assert np.all(recon.reconstructed_orig == 0)
    assert np.all(recon.reconstructed_mod == 0)

