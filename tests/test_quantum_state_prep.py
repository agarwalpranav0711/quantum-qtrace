"""
Tests for NEQR state preparation, coordinate mapping, and reversibility.
"""
import numpy as np
import pytest
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from src.quantum.state_prep import (
    coord_to_index,
    index_to_coord,
    index_to_pos_bits,
    apply_position_superposition,
    encode_image_into_register,
    uncompute_image_from_register,
)


def test_coordinate_mapping_roundtrip():
    for k in range(16):
        r, c = index_to_coord(k)
        assert 0 <= r < 4
        assert 0 <= c < 4
        assert coord_to_index(r, c) == k


def test_index_to_pos_bits():
    # k = 0 -> (0, 0, 0, 0)
    assert index_to_pos_bits(0) == (0, 0, 0, 0)
    # k = 6 (row 1, col 2) -> binary 0110 -> (0, 1, 1, 0)
    assert index_to_pos_bits(6) == (0, 1, 1, 0)
    # k = 15 -> (1, 1, 1, 1)
    assert index_to_pos_bits(15) == (1, 1, 1, 1)


def test_position_superposition_statevector():
    q_pos = QuantumRegister(4, name="pos")
    qc = QuantumCircuit(q_pos)
    apply_position_superposition(qc, q_pos)

    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities()
    assert len(probs) == 16
    # Each coordinate must have probability 1/16 = 0.0625
    expected_prob = 1.0 / 16.0
    for p in probs:
        assert np.isclose(p, expected_prob, atol=1e-6)


def test_image_encoding_and_uncomputation_reversibility():
    """
    Verifies that encoding an image and subsequently applying the uncomputing circuit
    returns the intensity register strictly to |0000> for every coordinate in superposition.
    """
    q_pos = QuantumRegister(4, name="pos")
    q_intensity = QuantumRegister(4, name="intensity")
    qc = QuantumCircuit(q_pos, q_intensity)

    # Prepare position superposition
    apply_position_superposition(qc, q_pos)

    # Arbitrary test image
    test_img = np.array([
        [1,  2,  3,  4],
        [5,  6,  7,  8],
        [9, 10, 11, 12],
        [13, 14, 15,  0]
    ], dtype=np.uint8)

    # Encode image
    encode_image_into_register(qc, test_img, q_pos, q_intensity)

    # Uncompute image
    uncompute_image_from_register(qc, test_img, q_pos, q_intensity)

    sv = Statevector.from_instruction(qc)
    # The intensity register must have returned to 0000_2
    # So all non-zero amplitudes must belong to states where intensity bits are 0.
    probs_dict = sv.probabilities_dict()
    for bitstring, prob in probs_dict.items():
        if prob > 1e-6:
            # bitstring is: intensity (4 bits) pos (4 bits)
            intensity_str = bitstring[0:4]
            assert intensity_str == "0000", f"Intensity register did not uncompute! Got {intensity_str}"

