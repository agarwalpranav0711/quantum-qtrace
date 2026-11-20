# Q-TRACE — Quantum Circuit Architecture & Gate Schematics

**Document ID:** `DOC-CIRC-001`  
**Classification:** Circuit Engineering & Hardware Layout Specification  
**Version:** 1.0.0 (Part 2 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Quantum Engineering Team  
**Scope:** Qubit Mapping, Gate Topologies, and Circuit Schematics for 16Q and 12Q Engines  

---

## 1. Register Architecture & Qubit Allocation

Q-TRACE implements two distinct circuit topologies for quantum image comparison:
1. **The Primary 16-Qubit Dedicated Register Topology**
2. **The Alternative 12-Qubit In-Place Topology**

### 1.1 Qubit Mapping Table (16-Qubit Circuit)

| Register | Qubit Index | Name | Role & Function | Physical Significance |
| :--- | :---: | :--- | :--- | :--- |
| **`pos`** | $q_0$ | `pos[0]` | Column Bit $x_0$ | Least significant column bit ($col = 2x_1 + x_0$) |
| **`pos`** | $q_1$ | `pos[1]` | Column Bit $x_1$ | Most significant column bit |
| **`pos`** | $q_2$ | `pos[2]` | Row Bit $y_0$ | Least significant row bit ($row = 2y_1 + y_0$) |
| **`pos`** | $q_3$ | `pos[3]` | Row Bit $y_1$ | Most significant row bit |
| **`orig`** | $q_4$ | `orig[0]` | Reference Intensity Bit $c_0$ | Least significant bit of Image A pixel value ($2^0$) |
| **`orig`** | $q_5$ | `orig[1]` | Reference Intensity Bit $c_1$ | Intensity bit $2^1$ |
| **`orig`** | $q_6$ | `orig[2]` | Reference Intensity Bit $c_2$ | Intensity bit $2^2$ |
| **`orig`** | $q_7$ | `orig[3]` | Reference Intensity Bit $c_3$ | Most significant bit of Image A ($2^3$) |
| **`mod`** | $q_8$ | `mod[0]` | Suspect Intensity Bit $c_0$ | Least significant bit of Image B pixel value ($2^0$) |
| **`mod`** | $q_9$ | `mod[1]` | Suspect Intensity Bit $c_1$ | Intensity bit $2^1$ |
| **`mod`** | $q_{10}$ | `mod[2]` | Suspect Intensity Bit $c_2$ | Intensity bit $2^2$ |
| **`mod`** | $q_{11}$ | `mod[3]` | Suspect Intensity Bit $c_3$ | Most significant bit of Image B ($2^3$) |
| **`diff`** | $q_{12}$ | `diff[0]` | XOR Difference Bit $d_0$ | Bitwise XOR output bit 0: $a_0 \oplus b_0$ |
| **`diff`** | $q_{13}$ | `diff[1]` | XOR Difference Bit $d_1$ | Bitwise XOR output bit 1: $a_1 \oplus b_1$ |
| **`diff`** | $q_{14}$ | `diff[2]` | XOR Difference Bit $d_2$ | Bitwise XOR output bit 2: $a_2 \oplus b_2$ |
| **`diff`** | $q_{15}$ | `diff[3]` | XOR Difference Bit $d_3$ | Bitwise XOR output bit 3: $a_3 \oplus b_3$ |

---

## 2. Circuit Execution Pipeline (16-Qubit)

```
STAGE 1: Superposition        STAGE 2: Coherent Dual Encoding         STAGE 3: CNOT XOR        STAGE 4: Measurement
+----------------------+   +------------------------------------+   +-------------------+   +--------------------+
|                      |   | For each pixel k in [0..15]:       |   | For bit j in 0..3:|   |                    |
| pos[0..3] --[ H ]----+-->| Condition on |k>_pos via X gates   |-->| CNOT(orig_j,diff_j)|-->| Measure pos -> c_pos|
|                      |   | MCX targeting orig[j] if A(k)_j=1  |   | CNOT(mod_j, diff_j)|   | Measure orig->c_orig|
|                      |   | MCX targeting mod[j]  if B(k)_j=1  |   |                   |   | Measure mod -> c_mod|
|                      |   | Invert X gates back                |   |                   |   | Measure diff->c_diff|
+----------------------+   +------------------------------------+   +-------------------+   +--------------------+
```

### 2.1 Bitwise CNOT XOR Comparison Schematic
For each bit position $j \in \{0, 1, 2, 3\}$:

```
|orig_j>  -------*----------------------  |orig_j>
                 |
|mod_j>   -------|-----------*----------  |mod_j>
                 |           |
|diff_j>  ------(+)---------(+)---------  |orig_j (+) mod_j>
```

Since $diff_j$ is initialized to $|0\rangle$:
1. Gate 1 ($CNOT(orig_j \to diff_j)$) copies bit $a_j$ onto $diff_j$: $|0\rangle \to |a_j\rangle$.
2. Gate 2 ($CNOT(mod_j \to diff_j)$) flips $diff_j$ if $b_j = 1$: $|a_j\rangle \to |a_j \oplus b_j\rangle$.

Total comparison gates: **8 CNOT gates** (2 per intensity bit $\times$ 4 bits).

---

## 3. The 12-Qubit In-Place Architecture

In the 12-qubit topology, the 4 dedicated difference qubits are eliminated. Instead, Register B is directly transformed in-place:

```
|orig_j>       -------*-------  |orig_j>
                      |
|mod_diff_j>   ------(+)------  |orig_j (+) mod_j>
```

Total comparison gates: **4 CNOT gates** (1 per intensity bit $\times$ 4 bits).

### Comparison Matrix:

| Architectural Metric | 16-Qubit Dedicated Register | 12-Qubit In-Place Register | Advantage / Trade-off |
| :--- | :--- | :--- | :--- |
| **Total Qubits** | 16 | 12 | 12Q saves 4 qubits (25% reduction) |
| **Total Classical Bits** | 16 | 12 | 12Q uses fewer measurement registers |
| **Statevector Memory** | 1.00 MiB (1.05 MB) | 64.00 KiB (65.54 KB) | **12Q achieves 93.75% memory reduction** |
| **XOR Gate Count** | 8 CNOTs | 4 CNOTs | 12Q requires 50% fewer comparison gates |
| **Typical Circuit Depth** | 247 | 247 | Identical depth (dominated by state prep) |
| **State Preservation** | Keeps Image A, B, and Diff | Overwrites Image B with Diff | **16Q is superior for visual educational inspection** |

---

## 4. Measurement Bit Ordering & Decoding Convention

Qiskit measures classical registers into space-separated bitstrings formatted from left to right as:
`'<m_diff> <m_mod> <m_orig> <m_pos>'`

- **Token 0 (Leftmost, 4 chars):** `m_diff` $\to$ Bitwise XOR difference integer $D \in [0, 15]$.
- **Token 1 (4 chars):** `m_mod` $\to$ Modified pixel intensity integer $B \in [0, 15]$ (omitted in 12Q).
- **Token 2 (4 chars):** `m_orig` $\to$ Original pixel intensity integer $A \in [0, 15]$.
- **Token 3 (Rightmost, 4 chars):** `m_pos` $\to$ Linear coordinate integer $k \in [0, 15]$.

### Coordinate Decoding Equations:
Given `pos_int = int(pos_str, 2)`:
$$\text{Row } Y = pos\_int // 4$$
$$\text{Col } X = pos\_int \% 4$$

Example measured bitstring: `'1011 1100 0111 0110'`
- `diff = 1011_2 = 11`
- `mod = 1100_2 = 12`
- `orig = 0111_2 = 7`
- `pos = 0110_2 = 6` $\implies$ Row $6 // 4 = 1$, Column $6 \% 4 = 2$.
- Verification: $7 \oplus 12 = 11$. Correct!

---

*Continue to `EXPERIMENT_RESULTS.md` for empirical experimental datasets and measured performance metrics.*

