"""
Quantum State Preparation module for NEQR Image Representation in Q-TRACE.
Implements reversible, unitary coordinate-conditioned intensity loading.
"""
from typing import List, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister


def coord_to_index(row: int, col: int) -> int:
    """Maps 2D matrix coordinate (row, col) in [0..3]x[0..3] to linear coordinate k in [0..15]."""
    if not (0 <= row < 4 and 0 <= col < 4):
        raise ValueError(f"Coordinates must be in [0, 3], got row={row}, col={col}")
    return 4 * row + col


def index_to_coord(k: int) -> Tuple[int, int]:
    """Maps linear coordinate k in [0..15] to 2D matrix coordinate (row, col)."""
    if not (0 <= k < 16):
        raise ValueError(f"Coordinate index k must be in [0, 15], got k={k}")
    return k // 4, k % 4


def index_to_pos_bits(k: int) -> Tuple[int, int, int, int]:
    """
    Returns the 4 position register bits (b0, b1, b2, b3) corresponding to coordinate k.
    
    Convention:
    - pos[0] = b0 = x_0 (column bit 0)
    - pos[1] = b1 = x_1 (column bit 1)
    - pos[2] = b2 = y_0 (row bit 0)
    - pos[3] = b3 = y_1 (row bit 1)
    
    k = 8*b3 + 4*b2 + 2*b1 + b0 = 4*row + col
    """
    b0 = k & 1
    b1 = (k >> 1) & 1
    b2 = (k >> 2) & 1
    b3 = (k >> 3) & 1
    return b0, b1, b2, b3


def apply_position_superposition(qc: QuantumCircuit, q_pos: QuantumRegister) -> None:
    r"""
    Applies Hadamard transforms across the 4 position qubits, creating an
    equiprobable spatial superposition of 16 coordinate basis states:
    
    (H^{\otimes 4}) |0000> = (1/4) \sum_{k=0}^{15} |k>
    """
    if len(q_pos) != 4:
        raise ValueError(f"Position register must contain 4 qubits, got {len(q_pos)}")
    for q in q_pos:
        qc.h(q)


def encode_image_into_register(
    qc: QuantumCircuit,
    image: np.ndarray,
    q_pos: QuantumRegister,
    q_intensity: QuantumRegister,
) -> None:
    """
    Encodes a 4x4 4-bit grayscale image into a target quantum intensity register
    conditioned on the 4-qubit spatial superposition register.
    
    For each coordinate k with intensity value C(k):
    For each bit j in [0..3]:
      If C(k)_j == 1: apply C^4(NOT) conditioned on |k>_pos targeting q_intensity[j].
    
    The operation is strictly unitary and reversible.
    """
    if image.shape != (4, 4):
        raise ValueError(f"Image must have shape (4, 4), got {image.shape}")
    if len(q_pos) != 4:
        raise ValueError(f"Position register must have 4 qubits, got {len(q_pos)}")
    if len(q_intensity) != 4:
        raise ValueError(f"Intensity register must have 4 qubits, got {len(q_intensity)}")

    for row in range(4):
        for col in range(4):
            k = coord_to_index(row, col)
            val = int(image[row, col])
            
            # If intensity is 0, all 4 bits are 0; no gates required for this basis state
            if val == 0:
                continue

            bits = index_to_pos_bits(k)
            inverted_qubit_indices = []

            # Invert position qubits where basis state bit is 0
            for idx, bit in enumerate(bits):
                if bit == 0:
                    qc.x(q_pos[idx])
                    inverted_qubit_indices.append(idx)

            # Apply multi-controlled NOT for each 1-bit in intensity value
            for j in range(4):
                if (val >> j) & 1:
                    qc.mcx(list(q_pos), q_intensity[j])

            # Revert position qubits to restore original coordinate basis
            for idx in inverted_qubit_indices:
                qc.x(q_pos[idx])


def uncompute_image_from_register(
    qc: QuantumCircuit,
    image: np.ndarray,
    q_pos: QuantumRegister,
    q_intensity: QuantumRegister,
) -> None:
    """
    Applies the exact Hermitian adjoint / inverse of the image encoding operation,
    reversibly returning the intensity register to |0000> across all superposition coordinates.
    Since MCX and X gates are their own inverses, we apply the operations in reverse order.
    """
    # Inverse of unitary loop over pixels
    for row in reversed(range(4)):
        for col in reversed(range(4)):
            k = coord_to_index(row, col)
            val = int(image[row, col])
            if val == 0:
                continue

            bits = index_to_pos_bits(k)
            inverted_qubit_indices = []

            for idx, bit in enumerate(bits):
                if bit == 0:
                    qc.x(q_pos[idx])
                    inverted_qubit_indices.append(idx)

            for j in reversed(range(4)):
                if (val >> j) & 1:
                    qc.mcx(list(q_pos), q_intensity[j])

            for idx in inverted_qubit_indices:
                qc.x(q_pos[idx])

