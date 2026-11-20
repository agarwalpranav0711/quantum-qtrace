"""
Quantum package initialization for Q-TRACE.
"""
from src.quantum.types import (
    PixelSample,
    ReconstructionResult,
    CircuitResources,
    QuantumComparisonOutput,
)
from src.quantum.state_prep import (
    coord_to_index,
    index_to_coord,
    index_to_pos_bits,
    apply_position_superposition,
    encode_image_into_register,
    uncompute_image_from_register,
)
from src.quantum.circuit_16q import QuantumComparator16Q
from src.quantum.circuit_12q import QuantumComparator12Q
from src.quantum.reconstruction import (
    decode_16q_bitstring,
    decode_12q_bitstring,
    reconstruct_from_counts,
    coupon_collector_expected_shots,
    coupon_collector_exact_probability,
    coupon_collector_poisson_approx,
)
from src.quantum.resource_estimator import (
    calculate_raw_statevector_memory,
    get_memory_scaling_table,
    benchmark_classical_vs_quantum,
)

