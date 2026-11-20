# Q-TRACE: Quantum Circuit Correctness & Unitary Reversibility Proofs

**Document Reference:** `docs/QUANTUM_CIRCUIT_CORRECTNESS.md`  
**Classification:** Quantum Mathematical Foundations  
**Version:** 1.9.0  

---

## 1. Unitary Formulation of NEQR Image Representation

Let a grayscale micro-patch of size $2^n \times 2^n$ be represented as an array of normalized pixel intensities $C_{YX} \in \{0, \dots, 2^q - 1\}$. In NEQR, the quantum state is defined as:

$$|\Psi\rangle = \frac{1}{2^n} \sum_{Y=0}^{2^n-1} \sum_{X=0}^{2^n-1} |YX\rangle \otimes |C_{YX}\rangle = \frac{1}{2^n} \sum_{Y=0}^{2^n-1} \sum_{X=0}^{2^n-1} |YX\rangle \otimes \bigotimes_{i=0}^{q-1} |C_{YX}^i\rangle$$

where $|YX\rangle = |Y_{n-1} \dots Y_0\rangle |X_{n-1} \dots X_0\rangle$ encodes the 2D spatial coordinate and $|C_{YX}^i\rangle \in \{|0\rangle, |1\rangle\}$ represents the $i$-th bit of the grayscale intensity.

For a $4 \times 4$ patch ($n = 2$, $N = 16$ pixels) with 4-bit intensity levels ($q = 4$):
- Spatial register: 4 qubits ($|Y_1 Y_0 X_1 X_0\rangle$).
- Intensity register: 4 qubits ($|C_3 C_2 C_1 C_0\rangle$).

---

## 2. Reversible XOR Difference Transformation

Quantum mechanics requires all non-measurement operations to be unitary and reversible ($U U^\dagger = I$).

### 2.1 16-Qubit Dedicated Difference Register
The joint state of original image $A$ and modified image $B$ prepared in superposition is:

$$|\Phi_0\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |A(k)\rangle_{orig} \otimes |B(k)\rangle_{mod} \otimes |0000\rangle_{diff}$$

The comparison unitary $U_{comp}$ applies transverse CNOT gates between corresponding intensity bits:

$$U_{comp} = \prod_{i=0}^{3} \text{CNOT}(orig_i \to diff_i) \cdot \text{CNOT}(mod_i \to diff_i)$$

Tracing the action on the difference register bit $diff_i$:
1. Initial state: $|0\rangle$.
2. After first CNOT: $|0 \oplus A_i(k)\rangle = |A_i(k)\rangle$.
3. After second CNOT: $|A_i(k) \oplus B_i(k)\rangle$.

The final state before measurement is:

$$|\Phi_1\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |A(k)\rangle_{orig} \otimes |B(k)\rangle_{mod} \otimes |A(k) \oplus B(k)\rangle_{diff}$$

### 2.2 Proof of Reversibility
Because $\text{CNOT}^{-1} = \text{CNOT}$, applying the exact same sequence of 8 CNOT gates in reverse order restores the dedicated difference register to $|0000\rangle$:

$$U_{comp}^\dagger U_{comp} = I_{16}$$

This confirms the circuit operates strictly within unitary quantum mechanics without non-physical state degradation.

