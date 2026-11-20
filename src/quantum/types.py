"""
Type definitions and dataclasses for Q-TRACE Quantum Image Processing.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


@dataclass
class PixelSample:
    """Represents the observed state of a single pixel from measurement shots."""
    row: int
    col: int
    coordinate_index: int
    observed_count: int
    orig_intensity: Optional[int] = None
    mod_intensity: Optional[int] = None
    diff_intensity: Optional[int] = None
    is_observed: bool = True
    is_tampered: bool = False


@dataclass
class ReconstructionResult:
    """Result of aggregating quantum measurement shots into reconstructed image maps."""
    reconstructed_orig: np.ndarray          # 4x4 array of original intensities (NaN/None represented as -1 if unobserved)
    reconstructed_mod: np.ndarray           # 4x4 array of modified intensities
    reconstructed_diff: np.ndarray          # 4x4 array of XOR difference values
    sampled_counts_map: np.ndarray          # 4x4 array of shot frequencies
    total_shots: int
    observed_coordinates_count: int        # Out of 16
    missing_coordinates: List[Tuple[int, int]]
    is_fully_reconstructed: bool
    pixel_samples: Dict[Tuple[int, int], PixelSample] = field(default_factory=dict)


@dataclass
class CircuitResources:
    """Hardware and simulation resources for a quantum circuit."""
    architecture_name: str
    num_qubits: int
    num_clbits: int
    circuit_depth: int
    total_gate_count: int
    gate_counts_by_type: Dict[str, int]
    two_qubit_gate_count: int               # CNOT / CX count
    multi_controlled_gate_count: int        # MCX count
    raw_statevector_memory_bytes: int
    simulation_runtime_seconds: float


@dataclass
class QuantumComparisonOutput:
    """Full execution output of a quantum image comparison run."""
    case_id: str
    architecture: str                       # '16-qubit' or '12-qubit'
    resources: CircuitResources
    reconstruction: ReconstructionResult
    classical_expected_diff: np.ndarray
    is_exact_match: bool                    # Compared to classical expected diff on observed pixels
    raw_counts: Dict[str, int]

