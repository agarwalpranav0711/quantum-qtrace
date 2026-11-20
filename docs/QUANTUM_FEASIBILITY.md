# Q-TRACE — Quantum Technical Feasibility & Circuit Architecture Report

**Document ID:** `DOC-KB-004`  
**Classification:** Quantum Computing & Mathematical Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Course Context:** Quantum Mechanics & Quantum Computing Capstone  

---

## 1. Executive Summary & Mathematical Objectives

This report provides the formal mathematical and quantum-circuit architecture for the experimental Quantum Image Processing (QIP) module in Q-TRACE. It evaluates the feasibility of the proposed **16-qubit NEQR image comparison architecture**, analyzes state preparation, multi-register entanglement, unitary XOR logic, measurement collapse dynamics, and reconstruction sampling statistics.

We rigorously demonstrate that:
1. The 16-qubit shared-position NEQR comparison circuit is **mathematically sound and fully reversible**.
2. An alternative **12-qubit in-place comparison circuit** reduces qubit overhead by 25% and state vector memory by 93.75%, serving as a high-efficiency alternative.
3. Measurement of a quantum superposition is subject to the **Coupon Collector's Problem**: a single shot yields only a single pixel's discrepancy. Complete $4 \times 4$ spatial reconstruction requires a minimum shot budget of $S \ge 155$ (for 99.9% completeness), with $S = 1024$ recommended as standard.
4. Global tamper detection can be augmented via an ancilla **Difference Flag qubit**, enabling single-shot zero-discrepancy verification and opening the door to **Grover-accelerated quadratic speedups**.

---

## 2. Formal Quantum State Representations

### 2.1 The NEQR Model for Grayscale Images

Let an image patch $I$ have spatial dimensions $2^n \times 2^n$ pixels (total pixels $N = 2^{2n}$) and a grayscale intensity resolution of $2^q$ levels (represented by $q$ bits, where pixel intensity $f(Y, X) \in \{0, 1, \dots, 2^q - 1\}$).

In the Novel Enhanced Quantum Representation (NEQR) framework (Zhang et al., 2013), the complete image is encoded into a normalized superposition state in the composite Hilbert space:
$$\mathcal{H} = \mathcal{H}_{intensity}^{\otimes q} \otimes \mathcal{H}_Y^{\otimes n} \otimes \mathcal{H}_X^{\otimes n}$$

The state vector is explicitly defined as:
$$|I\rangle = \frac{1}{\sqrt{2^{2n}}} \sum_{Y=0}^{2^n-1} \sum_{X=0}^{2^n-1} |f(Y, X)\rangle \otimes |Y\rangle \otimes |X\rangle$$

Where:
- $|Y\rangle = |y_{n-1} y_{n-2} \dots y_0\rangle$ and $|X\rangle = |x_{n-1} x_{n-2} \dots x_0\rangle$ are the spatial coordinate basis states.
- $|f(Y, X)\rangle = |c^{q-1}_{Y,X} c^{q-2}_{Y,X} \dots c^0_{Y,X}\rangle$ is the binary intensity value of the pixel at coordinate $(Y, X)$, with $c^j_{Y,X} \in \{0, 1\}$.

### 2.2 Mathematical Contrast: NEQR vs. FRQI vs. QPIE

```
+---------------------------------------------------------------------------------------------------+
|                           MATHEMATICAL COMPARISON OF QIP ENCODINGS                                |
+---------------------------------------------------------------------------------------------------+
| Feature               | FRQI (Le et al., 2011)        | QPIE / Amplitude Encoding | NEQR (Zhang et al., 2013) |
+-----------------------+-------------------------------+---------------------------+---------------------------+
| Intensity Storage     | Probability Amplitude (cos θ) | Normalized Amplitude c_i  | Computational Basis State |
| Total Qubit Count     | 2n + 1                        | 2n                        | 2n + q                    |
| Exact Pixel Arithmetic| IMPOSSIBLE (Requires State    | IMPOSSIBLE (Interferes    | TRIVIAL (Direct CNOT,     |
|                       | Tomography / Est. Angles)     | with Normalization)       | Toffoli, XOR Gates)       |
| Readout Efficiency    | Exponential Shots             | Exponential Shots         | Polynomial Basis Sampling |
| Reversibility of XOR  | N/A                           | N/A                       | Strictly Unitary & Pure   |
+---------------------------------------------------------------------------------------------------+
```

**Definitive Conclusion:** NEQR is the **only** representation that enables coherent, reversible, algebraic pixel-by-pixel comparisons ($D = A \oplus B$) on quantum hardware.

---

## 3. Circuit Architecture: The 16-Qubit Comparison Engine

The experimental target is a $4 \times 4$ image tile ($n = 2$, total pixels $N = 16$) with 4-bit grayscale intensity ($q = 4$, 16 gray levels from 0 to 15).

### 3.1 Register Allocation

```
Register Name   | Symbol | Qubits | Physical Interpretation
----------------+--------+--------+-------------------------------------------------------
Position Y      | |Y>    | 2      | Vertical coordinate row Y in {0, 1, 2, 3} (q0, q1)
Position X      | |X>    | 2      | Horizontal coordinate col X in {0, 1, 2, 3} (q2, q3)
Original Image  | |A>    | 4      | Reference pixel intensity f_A(Y,X) in {0..15} (q4..q7)
Modified Image  | |B>    | 4      | Suspect pixel intensity f_B(Y,X) in {0..15} (q8..q11)
Difference Map  | |D>    | 4      | Pixel-wise bitwise XOR: f_A (+) f_B (q12..q15)
----------------+--------+--------+-------------------------------------------------------
TOTAL           |        | 16     | State vector dimension = 2^16 = 65,536 complex amplitudes
```

### 3.2 Step-by-Step State Evolution

#### Step 1: Ground State Initialization
All 16 qubits are prepared in the computational zero ground state:
$$|\Psi_0\rangle = |0\rangle_A^{\otimes 4} \otimes |0\rangle_B^{\otimes 4} \otimes |0\rangle_D^{\otimes 4} \otimes |0\rangle_Y^{\otimes 2} \otimes |0\rangle_X^{\otimes 2} = |0\rangle^{\otimes 16}$$

#### Step 2: Spatial Superposition Generation
Hadamard transforms $H^{\otimes 4}$ are applied exclusively across the four position qubits ($Y$ and $X$):
$$|\Psi_1\rangle = (I^{\otimes 12} \otimes H^{\otimes 4}) |\Psi_0\rangle = |0\rangle_A^{\otimes 4} |0\rangle_B^{\otimes 4} |0\rangle_D^{\otimes 4} \otimes \left( \frac{1}{4} \sum_{Y=0}^3 \sum_{X=0}^3 |Y\rangle |X\rangle \right)$$

This creates an equiprobable superposition across all 16 spatial coordinates, with each coordinate state having amplitude $\alpha_k = \frac{1}{\sqrt{16}} = \frac{1}{4}$.

#### Step 3: Coherent Dual-Image Encoding
For each spatial coordinate $k = (Y, X)$ where $k \in \{0, 1, \dots, 15\}$:
Let $f_A(k) = a_3 a_2 a_1 a_0$ and $f_B(k) = b_3 b_2 b_1 b_0$.

We apply multi-controlled NOT gates conditioned on the position state $|k\rangle = |y_1 y_0 x_1 x_0\rangle$:
1. Apply Pauli-$X$ gates to all position qubits where the corresponding bit in the binary representation of $k$ is $0$.
2. For each bit $j \in \{0, 1, 2, 3\}$:
   - If the $j$-th bit of $f_A(k)$ is $1$ ($a_j = 1$): Apply a $C^4(NOT)$ gate targeting qubit $A_j$.
   - If the $j$-th bit of $f_B(k)$ is $1$ ($b_j = 1$): Apply a $C^4(NOT)$ gate targeting qubit $B_j$.
3. Re-apply Pauli-$X$ gates to the position qubits to restore their original basis representation.

After looping through all 16 pixels, the entangled quantum state is:
$$|\Psi_2\rangle = \frac{1}{4} \sum_{Y=0}^3 \sum_{X=0}^3 |f_A(Y,X)\rangle_A \otimes |f_B(Y,X)\rangle_B \otimes |0000\rangle_D \otimes |Y\rangle |X\rangle$$

**Crucial Insight:** The position register is strictly **shared** between Image A and Image B. This guarantees exact spatial correspondence without requiring independent coordinate entanglement.

#### Step 4: Unitary Quantum XOR Comparison
To compute the bitwise intensity difference $D = f_A(Y,X) \oplus f_B(Y,X)$ across all pixels simultaneously in superposition, we apply 8 CNOT gates targeting the Difference register $|D\rangle$:

For each bit position $j \in \{0, 1, 2, 3\}$:
1. $CNOT(\text{control} = A_j, \text{target} = D_j)$
2. $CNOT(\text{control} = B_j, \text{target} = D_j)$

Because $D_j$ is initialized to $|0\rangle$:
$$|0\rangle_{D_j} \xrightarrow{CNOT(A_j, D_j)} |a_j\rangle_{D_j} \xrightarrow{CNOT(B_j, D_j)} |a_j \oplus b_j\rangle_{D_j}$$

By linearity of quantum mechanics, this transformation acts concurrently on all basis states in superposition:
$$|\Psi_3\rangle = \frac{1}{4} \sum_{Y=0}^3 \sum_{X=0}^3 |f_A(Y,X)\rangle_A \otimes |f_B(Y,X)\rangle_B \otimes |f_A(Y,X) \oplus f_B(Y,X)\rangle_D \otimes |Y\rangle |X\rangle$$

```
Circuit Diagram Schematic (per bit j in superposition):

|A_j>   -----*-------------------  |A_j>
             |
|B_j>   -----+--------*----------  |B_j>
             |        |
|D_j>   ----(+)------(+)---------  |A_j (+) B_j>
```

---

## 4. Alternative Architecture: The 12-Qubit In-Place Engine

To reduce quantum simulator overhead on standard personal computers, we introduce the **12-Qubit In-Place Difference Engine**.

```
Register Name   | Symbol | Qubits | Description
----------------+--------+--------+---------------------------------------------
Position (Y, X) | |P>    | 4      | Spatial coordinates {0..15} (q0..q3)
Image A (Ref)   | |A>    | 4      | Reference intensity f_A (q4..q7)
Image B / Diff  | |B'>   | 4      | Target intensity transformed into f_A (+) f_B (q8..q11)
----------------+--------+--------+---------------------------------------------
TOTAL           |        | 12     | State vector = 2^12 = 4,096 complex amplitudes
```

### Mechanism:
Instead of allocating 4 dedicated difference qubits, CNOT gates are applied directly from Register $A$ to Register $B$:
$$CNOT(A_j, B_j): |b_j\rangle \to |a_j \oplus b_j\rangle$$

The resulting state is:
$$|\Psi_{12}\rangle = \frac{1}{4} \sum_{Y=0}^3 \sum_{X=0}^3 |f_A(Y,X)\rangle_A \otimes |f_A(Y,X) \oplus f_B(Y,X)\rangle_B \otimes |Y\rangle |X\rangle$$

### Architecture Comparison:

| Metric | 16-Qubit Register Architecture | 12-Qubit In-Place Architecture |
| :--- | :--- | :--- |
| **Qubit Count** | 16 | 12 (**25% reduction**) |
| **State Vector Dimensions** | $2^{16} = 65,536$ elements | $2^{12} = 4,096$ elements (**93.75% reduction**) |
| **Simulation Memory** | $\approx 1.05 \text{ MB}$ (complex128) | $\approx 65.5 \text{ KB}$ (complex128) |
| **State Preservation** | Keeps both Image A and Image B intact | Overwrites Image B with difference $D$ |
| **Gate Count for XOR** | 8 CNOTs | 4 CNOTs (**50% fewer comparison gates**) |
| **Academic Clarity** | Highly intuitive (separate input & output) | More compact, requires uncomputing to recover B |

**Recommendation:** Q-TRACE implements the **16-qubit architecture as the primary educational model** (for clear visualization of input vs. output registers) and the **12-qubit engine as the high-speed execution mode**.

---

## 5. Measurement Dynamics & Spatial Reconstruction

A central conceptual trap in quantum image processing is assuming that a single measurement of $|\Psi_3\rangle$ returns the complete difference map. **It does not.**

### 5.1 Single-Shot Wavefunction Collapse
When the position registers ($Y, X$) and difference register ($D$) are measured in the computational basis, Born's rule dictates that the superposition collapses to a **single** basis state:
$$|Y^*, X^*\rangle \otimes |D(Y^*, X^*)\rangle$$
with probability:
$$P(Y^*, X^*) = \left| \frac{1}{4} \right|^2 = \frac{1}{16} = 0.0625 \quad (6.25\%)$$

A single shot reveals the discrepancy value at **exactly one pixel**.

### 5.2 Multi-Shot Reconstruction: The Coupon Collector's Problem

Reconstructing the complete $4 \times 4$ spatial difference map requires sampling until all $N = 16$ distinct spatial coordinates have been observed at least once. This is mathematically governed by the **Coupon Collector's Problem**.

Let $T$ be the number of measurement shots required to collect all $N = 16$ distinct coordinates. The expected value $E[T]$ is:
$$E[T] = N \sum_{i=1}^N \frac{1}{i} = N \cdot H_N$$
where $H_{16}$ is the 16th harmonic number:
$$H_{16} = 1 + \frac{1}{2} + \frac{1}{3} + \dots + \frac{1}{16} \approx 3.3807$$
$$E[T] = 16 \times 3.3807 \approx 54.09 \text{ shots}$$

#### Variance and Tail Bounds for 99.9% Certainty:
The variance of the coupon collector time is:
$$\operatorname{Var}(T) = N^2 \sum_{i=1}^N \frac{1}{i^2} - N \cdot H_N \approx 16^2 \left( \frac{\pi^2}{6} \right) - 54.1 \approx 421 - 54.1 \approx 367$$

**Exact Probability via Inclusion-Exclusion:**
The exact analytical probability that all $N = 16$ spatial coordinates are sampled at least once in $S$ shots is:
$$P(\text{all } N \text{ observed}) = \sum_{j=0}^{16} (-1)^j \binom{16}{j} \left( \frac{16 - j}{16} \right)^S$$

Evaluating this exact summation yields:
- At $S = 54$ shots ($E[T]$): $P_{exact} = 59.10\%$
- At $S = 100$ shots: $P_{exact} = 97.50\%$
- At $S = 150$ shots: $P_{exact} = 99.9001\% \ge 99.9\%$
- At $S = 155$ shots: $P_{exact} = 99.9276\%$
- At $S = 256$ shots: $P_{exact} = 99.9999\%$
- At $S = 1024$ shots: $P_{exact} = 1.000000$ (Completeness certainty $1 - 10^{-27}$)

Using the classical Poisson tail approximation for rapid estimation:
$$P(\text{all } N \text{ states observed after } S \text{ shots}) \approx \exp\left( -N e^{-S / N} \right)$$
$$\exp\left( -16 e^{-S / 16} \right) \ge 0.999 \implies S \ge 16 \ln(16 / 0.001) \approx 154.9 \text{ shots}$$

**Engineering Rule for Q-TRACE:**
- Exact theoretical shots for 99.9% completeness: **150 shots** (approx. 155 shots).
- Recommended default Qiskit Aer shot budget: **1024 shots** ($P \approx 100\%$).
- Aggregated spatial reconstruction reconstructs $D(Y, X)$ with zero missing pixels while capturing realistic shot noise statistics.

---

## 6. Global Anomaly Detection & Grover Quadratic Speedup

In an insurance investigation, a primary triage question is:  
*"Is this $4 \times 4$ panel patch completely identical to the reference, or does any tampering exist?"*

### 6.1 The Discrepancy Flag Qubit
We append a single ancilla qubit $|Flag\rangle = |0\rangle$ to the circuit.

After computing register $|D\rangle = |d_3 d_2 d_1 d_0\rangle$, we apply a multi-qubit logical OR gate targeting $|Flag\rangle$:
- If $d_3 = d_2 = d_1 = d_0 = 0$ (pixel identical): $|Flag\rangle$ remains $|0\rangle$.
- If any $d_j = 1$ (pixel altered): $|Flag\rangle$ is flipped to $|1\rangle$.

```
Circuit:
|D_0> -----*-----
           |
|D_1> -----*-----
           |  (Multi-qubit OR)
|D_2> -----*-----
           |
|D_3> -----*-----
           |
|Flag> ---(+)----
```

### 6.2 Instant Zero-Discrepancy Certification
If Image A and Image B are **100% identical across all 16 pixels**, then for every basis state in superposition, $D = 0000_2$. Thus, $|Flag\rangle$ is never flipped.

**Result:** A **single measurement shot** yielding $|Flag\rangle = 0$ proves with mathematical certainty that **zero discrepancies exist in the entire patch**.

### 6.3 Grover Search for Sparse Tampering & The Uncomputing Oracle

If $M$ out of $N$ pixels are tampered with ($M \ge 1$), the state containing $|Flag\rangle = |1\rangle$ can be treated as a marked oracle state in **Grover's Algorithm**.

Instead of classically querying $O(N)$ pixels, Grover's diffusion operator amplifies the probability amplitudes of the tampered pixels in:
$$\mathcal{O}\left( \sqrt{\frac{N}{M}} \right) \text{ iterations}$$

For a $4 \times 4$ patch with 1 modified pixel ($N = 16, M = 1$):
$$\frac{\pi}{4} \sqrt{\frac{16}{1}} \approx \frac{\pi}{4} \times 4 \approx 3.14 \implies \mathbf{3 \text{ Grover iterations}}$$

#### Critical Quantum Mechanics Constraint: The Uncomputing Oracle Requirement
A common theoretical error in quantum image processing is attempting to apply Grover's diffusion operator $D_{pos} = 2|s\rangle\langle s| - I$ directly to the position register while it remains entangled with the image and difference registers.

If the registers remain entangled:
$$|\Psi\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k), f_B(k), D(k)\rangle$$
The reduced density matrix of the position register is a **mixed state**, which destroys constructive quantum interference. Applying diffusion directly without uncomputing yields only $\approx 62.5\%$ probability on the marked state.

**The Valid Grover Oracle Protocol:**
To achieve 100% constructive interference, Q-TRACE implements an **uncomputing oracle**:
$$U_{oracle} = U_{prep}^\dagger \cdot U_{phase\_kickback} \cdot U_{prep}$$
1. $U_{prep}$: Encodes the image pixel intensities and calculates register $|D\rangle$.
2. $U_{phase\_kickback}$: Applies a phase inversion $(-1)$ via an ancilla in state $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ conditioned on $|D\rangle \neq 0$.
3. $U_{prep}^\dagger$: Reversibly uncomputes the intensity and difference registers back to $|0\rangle^{\otimes 12}$.

This returns the composite state to:
$$|\Psi_{marked}\rangle = \left( \frac{1}{4} \sum_{k=0}^{15} (-1)^{\mathbb{I}(D(k) \neq 0)} |k\rangle_{pos} \right) \otimes |0\rangle^{\otimes 12}$$
Because the position register is now strictly unentangled, Grover's standard diffusion operator $H^{\otimes 4} (2|0\rangle\langle 0| - I) H^{\otimes 4}$ amplifies the marked tampered pixel to **100.0% probability**.

---

## 7. Resource Requirements & Classical Simulator Limits

### 7.1 Scalability Analysis: Why Forensic Patch Tiling is Mandatory

```
Image Tile Size | Intensity (q) | Position (2n) | Total Qubits | Statevector RAM (Binary) | Statevector RAM (Decimal) | Feasibility
----------------+---------------+---------------+--------------+--------------------------+---------------------------+-------------------
4 x 4           | 4-bit         | 4             | 16           | 1.00 MiB                 | 1.05 MB                   | Fast Local Sim (<150 ms)
4 x 4           | 8-bit         | 4             | 28           | 4.00 GiB                 | 4.29 GB                   | Laptop RAM limit
8 x 8           | 4-bit         | 6             | 18           | 4.00 MiB                 | 4.19 MB                   | Feasible Sim (<400 ms)
8 x 8           | 8-bit         | 6             | 30           | 16.00 GiB                | 17.18 GB                  | Workstation RAM
16 x 16         | 8-bit         | 8             | 32           | 64.00 GiB                | 68.72 GB                  | Server required
512 x 512       | 8-bit         | 18            | 42           | 64.00 TiB                | 70.37 TB                  | IMPOSSIBLE on laptop
12 MP (4k x 3k) | 8-bit         | 24            | 48           | 4,096.00 TiB (4.0 PiB)   | 4.50 Petabytes            | IMPOSSIBLE on Earth
```

**Scientific Reality:** Simulating a full 512x512 image in NEQR classically requires 64 TiB (70.37 TB) of RAM, and a full 12-megapixel photograph requires **4.5 Petabytes of RAM**. This confirms why claiming "full-image quantum forensics" on a student laptop is scientifically impossible.

**Q-TRACE's Forensic Patch Tiling Strategy** is the scientifically sound answer:
1. The Classical Engine scans the full 12-megapixel photograph and identifies high-suspicion clusters.
2. The user or automated pipeline crops a $4 \times 4$ or $8 \times 8$ grayscale patch from the suspicious region.
3. The Quantum Laboratory ingests this tile into the 16-qubit Qiskit Aer circuit, executing complete state preparation, XOR, and Grover search within 150 milliseconds.

---

## 8. Summary of Answers to Critical Research Questions

1. **Position Superposition:** Prepared via $H^{\otimes 4}$ on spatial qubits ($q_0..q_3$).
2. **Dual-Image Encoding:** Conditioned multi-controlled NOTs ($C^4(NOT)$) mapping $f_A(k)$ into Register A and $f_B(k)$ into Register B.
3. **Pixel Correspondence:** Guaranteed by binding both image registers to the **same** position register.
4. **Coherent Comparison:** Executed via 8 CNOTs from $A_j$ and $B_j$ to $D_j$, performing bitwise XOR.
5. **Register Validity:** Fully validated. 16 qubits total (4 pos, 4 orig, 4 mod, 4 diff).
6. **Ancilla Requirements:** Zero ancilla required for basic XOR; 1 optional ancilla for global discrepancy flag.
7. **Reversibility:** Strictly preserved; all gates are unitary ($H, X, CNOT$).
8. **Measurement:** Measures position and difference registers in computational basis.
9. **One-Shot Information:** Yields exactly one pixel coordinate and its difference value ($P = 6.25\%$).
10. **Reconstruction:** Aggregated over 1024 shots governed by the Coupon Collector's distribution ($S \ge 155$ for 99.9% completeness).
11. **Scalability:** Requires $2n + 3q$ qubits.
12. **Gate Count:** $\approx 16 \times (4+4) = 128$ multi-controlled gates for state prep + 8 CNOTs for comparison.
13. **State Prep Cost:** $O(q \cdot 2^{2n})$, the dominant bottleneck.
14. **Information Lost:** Individual intermediate amplitudes are collapsed upon measurement, but statistical basis reconstruction recovers the complete difference matrix.

---

*Continue to `CLASSICAL_FORENSICS.md` for the classical forensic algorithm study.*

