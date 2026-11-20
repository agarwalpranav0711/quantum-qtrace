"""
16-Qubit NEQR Image Comparison Circuit for Q-TRACE.
Implements the primary dedicated-register difference architecture.
"""
from typing import Tuple, Dict, Any, Optional
import time
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

from src.quantum.state_prep import (
    apply_position_superposition,
    encode_image_into_register,
)
from src.quantum.types import CircuitResources


class QuantumComparator16Q:
    """
    16-Qubit NEQR Image Comparison Circuit Builder and Runner.
    
    Register Layout:
    - Position Register (pos): 4 qubits (q0..q3) -> 16 coordinates
    - Original Image Register (orig): 4 qubits (q4..q7) -> Reference intensities
    - Modified Image Register (mod): 4 qubits (q8..q11) -> Suspect intensities
    - Difference Register (diff): 4 qubits (q12..q15) -> Bitwise XOR difference
    - Classical Measurement Registers (c_pos, c_orig, c_mod, c_diff): 16 bits total
    """

    def __init__(self, img_orig: np.ndarray, img_mod: np.ndarray):
        if img_orig.shape != (4, 4) or img_mod.shape != (4, 4):
            raise ValueError("Both images must be 4x4 2D numpy arrays")
        self.img_orig = img_orig
        self.img_mod = img_mod

    def build_circuit(self, with_measurements: bool = True) -> QuantumCircuit:
        """
        Constructs the complete 16-qubit quantum comparison circuit.
        """
        q_pos = QuantumRegister(4, name="pos")
        q_orig = QuantumRegister(4, name="orig")
        q_mod = QuantumRegister(4, name="mod")
        q_diff = QuantumRegister(4, name="diff")

        if with_measurements:
            c_pos = ClassicalRegister(4, name="m_pos")
            c_orig = ClassicalRegister(4, name="m_orig")
            c_mod = ClassicalRegister(4, name="m_mod")
            c_diff = ClassicalRegister(4, name="m_diff")
            qc = QuantumCircuit(
                q_pos, q_orig, q_mod, q_diff,
                c_pos, c_orig, c_mod, c_diff
            )
        else:
            qc = QuantumCircuit(q_pos, q_orig, q_mod, q_diff)

        # Stage 1: Position superposition
        apply_position_superposition(qc, q_pos)

        # Stage 2: Dual-image coherent encoding
        encode_image_into_register(qc, self.img_orig, q_pos, q_orig)
        encode_image_into_register(qc, self.img_mod, q_pos, q_mod)

        # Stage 3: Bitwise CNOT XOR Comparison
        # D_j = A_j XOR B_j
        for j in range(4):
            qc.cx(q_orig[j], q_diff[j])
            qc.cx(q_mod[j], q_diff[j])

        # Stage 4: Measurements (if requested)
        if with_measurements:
            qc.measure(q_pos, c_pos)
            qc.measure(q_orig, c_orig)
            qc.measure(q_mod, c_mod)
            qc.measure(q_diff, c_diff)

        return qc

    def extract_resources(self, runtime_seconds: float = 0.0) -> CircuitResources:
        """Calculates exact gate counts, circuit depth, and memory resources."""
        qc = self.build_circuit(with_measurements=True)
        gate_counts = dict(qc.count_ops())
        depth = qc.depth()
        total_gates = sum(gate_counts.values())
        two_qubit_gates = gate_counts.get("cx", 0)
        mcx_gates = gate_counts.get("mcx", 0)

        # Memory for 16-qubit statevector: 2^16 complex128 numbers (16 bytes each) = 1.05 MB
        raw_memory_bytes = (2 ** 16) * 16

        return CircuitResources(
            architecture_name="16-qubit NEQR Dedicated Register",
            num_qubits=16,
            num_clbits=16,
            circuit_depth=depth,
            total_gate_count=total_gates,
            gate_counts_by_type=gate_counts,
            two_qubit_gate_count=two_qubit_gates,
            multi_controlled_gate_count=mcx_gates,
            raw_statevector_memory_bytes=raw_memory_bytes,
            simulation_runtime_seconds=runtime_seconds,
        )

    def run_simulation(
        self,
        shots: int = 1024,
        seed_simulator: Optional[int] = None,
    ) -> Tuple[Dict[str, int], CircuitResources]:
        """
        Executes the circuit on Qiskit AerSimulator.
        
        Returns:
            Tuple of (raw measurement counts dictionary, CircuitResources).
        """
        qc = self.build_circuit(with_measurements=True)
        sim = AerSimulator()

        start_time = time.perf_counter()
        job = sim.run(qc, shots=shots, seed_simulator=seed_simulator)
        result = job.result()
        elapsed = time.perf_counter() - start_time

        counts = result.get_counts()
        resources = self.extract_resources(runtime_seconds=elapsed)
        return counts, resources

