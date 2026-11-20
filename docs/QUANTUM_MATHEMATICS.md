# Q-TRACE — Quantum Mathematical Foundations & State Derivations

**Document ID:** `DOC-MATH-001`  
**Classification:** Theoretical Physics & Mathematical Proof Specification  
**Version:** 1.0.0 (Part 2 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Quantum Engineering Team  
**Scope:** Formal Derivations of NEQR, Unitary Gate Decompositions, and Measurement Dynamics  

---

## 1. Mathematical Formulation of the NEQR State

Digital image representation in the Novel Enhanced Quantum Representation (NEQR) framework (Zhang et al., 2013) encodes an image of dimensions $2^n \times 2^n$ pixels with $q$-bit grayscale intensity levels into an entangled quantum state spanning a composite Hilbert space:
$$\mathcal{H} = \mathcal{H}_{intensity}^{\otimes q} \otimes \mathcal{H}_Y^{\otimes n} \otimes \mathcal{H}_X^{\otimes n}$$

For a $4 \times 4$ image ($n = 2$, total pixels $N = 2^{2 \times 2} = 16$) with 4-bit grayscale intensity ($q = 4$, values in $\{0, 1, \dots, 15\}$), the state is defined as:
$$|I\rangle = \frac{1}{\sqrt{16}} \sum_{Y=0}^3 \sum_{X=0}^3 |f(Y, X)\rangle \otimes |Y\rangle \otimes |X\rangle = \frac{1}{4} \sum_{k=0}^{15} |f(k)\rangle \otimes |k\rangle_{pos}$$

Where:
- Coordinate basis state $|k\rangle_{pos} = |y_1 y_0 x_1 x_0\rangle \in \{|0\rangle, \dots, |15\rangle\}$ maps to spatial coordinate $(Y, X) = (k // 4, k \% 4)$.
- Intensity basis state $|f(k)\rangle = |c_3 c_2 c_1 c_0\rangle \in \{|0\rangle, \dots, |15\rangle\}$ encodes the binary pixel value:
  $$f(k) = \sum_{j=0}^3 c_j 2^j, \quad c_j \in \{0, 1\}$$

---

## 2. Derivation of the 16-Qubit Comparison Engine

The composite Hilbert space for the 16-qubit system is:
$$\mathcal{H}_{total} = \mathcal{H}_{pos}^{\otimes 4} \otimes \mathcal{H}_{orig}^{\otimes 4} \otimes \mathcal{H}_{mod}^{\otimes 4} \otimes \mathcal{H}_{diff}^{\otimes 4} \quad (\dim = 2^{16} = 65,536)$$

### Step 1: Ground State Initialization
All 16 qubits are prepared in the computational zero ground state:
$$|\Psi_0\rangle = |0\rangle^{\otimes 16} = |0\rangle_{pos}^{\otimes 4} \otimes |0\rangle_{orig}^{\otimes 4} \otimes |0\rangle_{mod}^{\otimes 4} \otimes |0\rangle_{diff}^{\otimes 4}$$

### Step 2: Spatial Superposition Generation
Hadamard transforms are applied exclusively to the 4 position qubits:
$$H^{\otimes 4} |0000\rangle_{pos} = \left(\frac{|0\rangle + |1\rangle}{\sqrt{2}}\right) \otimes \left(\frac{|0\rangle + |1\rangle}{\sqrt{2}}\right) \otimes \left(\frac{|0\rangle + |1\rangle}{\sqrt{2}}\right) \otimes \left(\frac{|0\rangle + |1\rangle}{\sqrt{2}}\right) = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos}$$

The composite state becomes:
$$|\Psi_1\rangle = \left( \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \right) \otimes |0000\rangle_{orig} \otimes |0000\rangle_{mod} \otimes |0000\rangle_{diff}$$

### Step 3: Coherent Dual-Image Encoding
For each coordinate $k \in \{0, \dots, 15\}$, let $k = (b_3, b_2, b_1, b_0)_2$. We define the coordinate projection operator:
$$\Pi_k = |k\rangle\langle k|_{pos}$$
The unitary image loading operation $U_{prep}$ is defined as:
$$U_{prep} = \sum_{k=0}^{15} |k\rangle\langle k|_{pos} \otimes U_A(k) \otimes U_B(k) \otimes I_{diff}$$
where:
$$U_A(k) = \bigotimes_{j=0}^3 X^{f_A(k)_j}, \quad U_B(k) = \bigotimes_{j=0}^3 X^{f_B(k)_j}$$
with $f_A(k)_j, f_B(k)_j \in \{0, 1\}$ denoting the $j$-th bit of intensity values $f_A(k)$ and $f_B(k)$.

Applying $U_{prep}$ to $|\Psi_1\rangle$:
$$|\Psi_2\rangle = U_{prep} |\Psi_1\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k)\rangle_{orig} \otimes |f_B(k)\rangle_{mod} \otimes |0000\rangle_{diff}$$

#### Proof of State Normalization:
Since $\{|k\rangle_{pos}\}$ forms an orthonormal basis ($\langle j | k \rangle_{pos} = \delta_{jk}$) and the intensity vectors are computational basis states ($\langle f_A(k) | f_A(k) \rangle = 1$):
$$\langle \Psi_2 | \Psi_2 \rangle = \frac{1}{16} \sum_{j=0}^{15} \sum_{k=0}^{15} \langle j | k \rangle_{pos} \langle f_A(j) | f_A(k) \rangle \langle f_B(j) | f_B(k) \rangle \langle 0000 | 0000 \rangle$$
$$= \frac{1}{16} \sum_{k=0}^{15} 1 = \frac{16}{16} = 1$$
Normalization is strictly preserved.

### Step 4: Unitary Quantum XOR Comparison
To calculate $D_j = A_j \oplus B_j$, we apply 8 CNOT gates targeting register $|D\rangle$:
$$U_{XOR} = \prod_{j=0}^3 CNOT(orig_j \to diff_j) \cdot CNOT(mod_j \to diff_j)$$

For an arbitrary computational basis state $|k\rangle |a\rangle |b\rangle |0\rangle$:
For bit position $j$:
$$|a_j\rangle |b_j\rangle |0\rangle_{diff_j} \xrightarrow{CNOT(orig_j \to diff_j)} |a_j\rangle |b_j\rangle |a_j\rangle_{diff_j} \xrightarrow{CNOT(mod_j \to diff_j)} |a_j\rangle |b_j\rangle |a_j \oplus b_j\rangle_{diff_j}$$

Because $U_{XOR}$ acts linearly across all terms in superposition:
$$|\Psi_3\rangle = U_{XOR} |\Psi_2\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k)\rangle_{orig} \otimes |f_B(k)\rangle_{mod} \otimes |f_A(k) \oplus f_B(k)\rangle_{diff}$$

---

## 3. Derivation of the 12-Qubit In-Place Difference Engine

The 12-qubit architecture eliminates the dedicated difference register:
$$\mathcal{H}_{12} = \mathcal{H}_{pos}^{\otimes 4} \otimes \mathcal{H}_{orig}^{\otimes 4} \otimes \mathcal{H}_{mod\_diff}^{\otimes 4} \quad (\dim = 2^{12} = 4,096)$$

### State Evolution:
1. Superposition and dual encoding prepare:
   $$|\Phi_1\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k)\rangle_{orig} \otimes |f_B(k)\rangle_{mod\_diff}$$
2. In-place CNOT gates target register $|mod\_diff\rangle$ directly:
   $$U_{in\_place} = \prod_{j=0}^3 CNOT(orig_j \to mod\_diff_j)$$
   $$|a_j\rangle |b_j\rangle \xrightarrow{CNOT(orig_j \to mod\_diff_j)} |a_j\rangle |a_j \oplus b_j\rangle$$
3. The resulting state is:
   $$|\Phi_2\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k)\rangle_{orig} \otimes |f_A(k) \oplus f_B(k)\rangle_{mod\_diff}$$

### Proof of Reversibility:
Because CNOT is its own inverse ($CNOT^2 = I$):
$$U_{in\_place}^\dagger = U_{in\_place}$$
Applying $U_{in\_place}$ a second time yields:
$$|a_j\rangle |a_j \oplus b_j\rangle \to |a_j\rangle |(a_j \oplus b_j) \oplus a_j\rangle = |a_j\rangle |b_j\rangle$$
This mathematically proves that the in-place transformation is strictly reversible, and Image B can be recovered without information loss prior to measurement.

---

## 4. Measurement Dynamics & Probability Derivations

### 4.1 Born's Rule & Single-Shot Probability
When measuring the 16 qubits in the computational basis $\{|k, a, b, d\rangle\}$, the probability of observing outcome $(k^*, a^*, b^*, d^*)$ is:
$$P(k^*, a^*, b^*, d^*) = |\langle k^*, a^*, b^*, d^* | \Psi_3 \rangle|^2$$
$$= \left| \frac{1}{4} \delta_{a^*, f_A(k^*)} \delta_{b^*, f_B(k^*)} \delta_{d^*, f_A(k^*) \oplus f_B(k^*)} \right|^2$$
$$P(k^*) = \left(\frac{1}{4}\right)^2 = \frac{1}{16} = 0.0625 \quad (6.25\%)$$

The spatial distribution across all 16 coordinates is strictly uniform: each shot independently samples one coordinate $k \in \{0, \dots, 15\}$ with probability $p = 1/16$.

---

## 5. Coupon Collector Sampling Theory

### 5.1 Expected Number of Measurement Shots
Let random variable $T$ be the number of shots required to observe all $N = 16$ coordinates.
Let $T_i$ be the additional shots required to find the $i$-th new coordinate after $i - 1$ distinct coordinates have been found.
$T_i$ follows a geometric distribution with success probability $p_i = \frac{N - (i - 1)}{N}$.
The expected value is:
$$E[T_i] = \frac{1}{p_i} = \frac{N}{N - i + 1}$$
By linearity of expectation:
$$E[T] = \sum_{i=1}^N E[T_i] = \sum_{i=1}^N \frac{N}{N - i + 1} = N \sum_{m=1}^N \frac{1}{m} = N \cdot H_N$$
For $N = 16$:
$$H_{16} = 1 + \frac{1}{2} + \frac{1}{3} + \dots + \frac{1}{16} = \frac{729653}{216000} \approx 3.380729$$
$$E[T] = 16 \times 3.380729 = \mathbf{54.09166 \text{ shots}}$$

### 5.2 Exact Analytical Probability of Complete Coverage
Using the principle of inclusion-exclusion, the exact probability that all $N = 16$ coordinates are sampled at least once after $S$ independent shots is:
$$P(\text{all } N \text{ collected}) = \sum_{j=0}^N (-1)^j \binom{N}{j} \left( \frac{N - j}{N} \right)^S$$

For $N = 16$:
$$P(16, S) = \sum_{j=0}^{16} (-1)^j \binom{16}{j} \left( \frac{16 - j}{16} \right)^S$$

### 5.3 Poisson Tail Approximation
For large $S$, the probability that a specific coordinate remains unobserved after $S$ trials is $\left(1 - \frac{1}{N}\right)^S \approx e^{-S/N}$.
The number of unobserved coordinates approximately follows a Poisson distribution with mean $\lambda = N e^{-S/N}$.
The probability of zero unobserved coordinates is:
$$P(0 \text{ missing}) = e^{-\lambda} = \exp\left( -N e^{-S / N} \right)$$

To achieve $P \ge 0.999$:
$$-N e^{-S / N} \ge \ln(0.999) \implies S \ge N \ln\left( \frac{N}{-\ln(0.999)} \right)$$
$$S \ge 16 \ln\left( \frac{16}{0.0010005} \right) \approx 16 \ln(15992) \approx 16 \times 9.680 \approx \mathbf{154.9 \text{ shots}}$$

---

*Continue to `CIRCUIT_ARCHITECTURE.md` for gate layout, qubit allocations, and circuit schematics.*

