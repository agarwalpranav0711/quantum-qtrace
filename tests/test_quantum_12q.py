"""
Tests for the 12-qubit in-place NEQR comparison engine.
"""
import numpy as np
import pytest

from src.classical.test_data import (
    create_test_case_identical,
    create_test_case_single_pixel,
    create_test_case_full_change,
)
from src.classical.comparator import classical_xor_difference
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import reconstruct_from_counts


def test_12q_circuit_structure():
    tc = create_test_case_single_pixel()
    comp = QuantumComparator12Q(tc["img_a"], tc["img_b"])
    qc = comp.build_circuit(with_measurements=True)

    assert qc.num_qubits == 12
    assert qc.num_clbits == 12

    qc_no_meas = comp.build_circuit(with_measurements=False)
    assert qc_no_meas.num_qubits == 12
    assert qc_no_meas.num_clbits == 0


def test_12q_resource_extraction():
    tc = create_test_case_single_pixel()
    comp = QuantumComparator12Q(tc["img_a"], tc["img_b"])
    res = comp.extract_resources()

    assert res.num_qubits == 12
    assert res.num_clbits == 12
    assert res.two_qubit_gate_count == 4  # 4 in-place CNOTs (half of 16-qubit's 8)
    assert res.raw_statevector_memory_bytes == 2**12 * 16  # 64 KB


def test_12q_single_pixel_difference():
    tc = create_test_case_single_pixel()
    comp = QuantumComparator12Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=101)
    recon = reconstruct_from_counts(counts, architecture="12-qubit", total_shots=1024)

    expected_diff = classical_xor_difference(tc["img_a"], tc["img_b"])
    assert np.array_equal(recon.reconstructed_diff, expected_diff)
    assert recon.reconstructed_diff[1, 2] == 11
    assert np.count_nonzero(recon.reconstructed_diff) == 1


def test_12q_identical_images():
    tc = create_test_case_identical()
    comp = QuantumComparator12Q(tc["img_a"], tc["img_b"])
    counts, _ = comp.run_simulation(shots=1024, seed_simulator=202)
    recon = reconstruct_from_counts(counts, architecture="12-qubit", total_shots=1024)

    assert np.all(recon.reconstructed_diff == 0)


def test_12q_in_place_reversibility():
    """
    Verifies that applying uncompute_diff=True restores Image B in the target register,
    proving physical and mathematical reversibility of the in-place transformation.
    """
    tc = create_test_case_single_pixel()
    comp = QuantumComparator12Q(tc["img_a"], tc["img_b"])
    # With uncompute_diff=True, the second CNOT pass undoes the XOR, restoring Image B
    qc = comp.build_circuit(with_measurements=True, uncompute_diff=True)
    
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    counts = sim.run(qc, shots=1024, seed_simulator=303).result().get_counts()
    
    # When uncomputed, the register measured into m_diff holds Image B again!
    recon = reconstruct_from_counts(counts, architecture="12-qubit", total_shots=1024)
    assert np.array_equal(recon.reconstructed_diff, tc["img_b"])

