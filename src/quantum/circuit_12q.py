"""
12-Qubit NEQR In-Place Image Comparison Circuit for Q-TRACE.
Implements the memory-efficient in-place difference architecture.
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


class QuantumComparator12Q:
    """
    12-Qubit NEQR In-Place Image Comparison Circuit Builder and Runner.
    
    Register Layout:
    - Position Register (pos): 4 qubits (q0..q3) -> 16 coordinates
    - Original Image Register (orig): 4 qubits (q4..q7) -> Reference intensities
    - Modified / Diff Register (mod_diff): 4 qubits (q8..q11) -> Target transformed in-place
    - Classical Measurement Registers (c_pos, c_orig, c_diff): 12 bits total
    
    Memory Advantage:
    - 12 qubits: 2^12 = 4,096 statevector amplitudes (64 KB at complex128).
    - 93.75% memory reduction compared to 16 qubits.
    """

    def __init__(self, img_orig: np.ndarray, img_mod: np.ndarray):
        if img_orig.shape != (4, 4) or img_mod.shape != (4, 4):
            raise ValueError("Both images must be 4x4 2D numpy arrays")
        self.img_orig = img_orig
        self.img_mod = img_mod

    def build_circuit(
        self,
        with_measurements: bool = True,
        uncompute_diff: bool = False,
    ) -> QuantumCircuit:
        """
        Constructs the 12-qubit in-place quantum comparison circuit.
        
        Args:
            with_measurements: Whether to append classical measurement gates.
            uncompute_diff: If True, applies second CNOT pass to restore Image B in-place.
        """
        q_pos = QuantumRegister(4, name="pos")
        q_orig = QuantumRegister(4, name="orig")
        q_mod_diff = QuantumRegister(4, name="mod_diff")

        if with_measurements:
            c_pos = ClassicalRegister(4, name="m_pos")
            c_orig = ClassicalRegister(4, name="m_orig")
            c_diff = ClassicalRegister(4, name="m_diff")
            qc = QuantumCircuit(q_pos, q_orig, q_mod_diff, c_pos, c_orig, c_diff)
        else:
            qc = QuantumCircuit(q_pos, q_orig, q_mod_diff)

        # Stage 1: Position superposition
        apply_position_superposition(qc, q_pos)

        # Stage 2: Dual-image coherent encoding
        encode_image_into_register(qc, self.img_orig, q_pos, q_orig)
        encode_image_into_register(qc, self.img_mod, q_pos, q_mod_diff)

        # Stage 3: In-Place CNOT XOR Comparison
        # mod_diff_j = orig_j XOR mod_diff_j
        for j in range(4):
            qc.cx(q_orig[j], q_mod_diff[j])

        # Optional uncomputing pass (demonstrating reversibility)
        if uncompute_diff:
            for j in range(4):
                qc.cx(q_orig[j], q_mod_diff[j])

        # Stage 4: Measurements (if requested)
        if with_measurements:
            qc.measure(q_pos, c_pos)
            qc.measure(q_orig, c_orig)
            qc.measure(q_mod_diff, c_diff)

        return qc

    def extract_resources(self, runtime_seconds: float = 0.0) -> CircuitResources:
        """Calculates exact gate counts, circuit depth, and memory resources."""
        qc = self.build_circuit(with_measurements=True)
        gate_counts = dict(qc.count_ops())
        depth = qc.depth()
        total_gates = sum(gate_counts.values())
        two_qubit_gates = gate_counts.get("cx", 0)
        mcx_gates = gate_counts.get("mcx", 0)

        # Memory for 12-qubit statevector: 2^12 complex128 numbers (16 bytes each) = 64 KB
        raw_memory_bytes = (2 ** 12) * 16

        return CircuitResources(
            architecture_name="12-qubit NEQR In-Place Register",
            num_qubits=12,
            num_clbits=12,
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
        Executes the 12-qubit circuit on Qiskit AerSimulator.
        
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

