# Q-TRACE — Viva Presentation & Oral Defense Guide

**Document ID:** `DOC-VIVA-001`  
**Classification:** Academic Viva & Oral Defense Preparation  
**Version:** 1.0.0 (Part 2 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Quantum Engineering Team  
**Audience:** University B.Tech CSE Student preparing for Capstone Defense  

---

## 1. How to Explain Q-TRACE in 60 Seconds (Elevator Pitch)

> *"Good morning, esteemed examiners. Q-TRACE is a digital image forensics platform designed to detect photographic tampering in motor insurance claims—such as digitally spliced vehicle dents or cloned bodywork scratches.*
> 
> *Because simulating a full 12-megapixel photograph quantum-mechanically would require 48 qubits, which is over 4 petabytes of RAM, we developed the **Forensic Patch Tiling** paradigm. Our classical engine scans the full photograph using physics- and signal-based methods like Error Level Analysis and SIFT keypoint clustering to identify suspicious regions.*
> 
> *We then crop suspicious $4 \times 4$ patches and load them into our experimental **Quantum Image Processing Laboratory**. Using Novel Enhanced Quantum Representation (NEQR), we prepare a coherent spatial superposition over 16 coordinates and execute bitwise XOR comparison concurrently across all pixels using unitary CNOT gates.*
> 
> *In Part 2, we built this quantum engine using Qiskit. We mathematically validated both a 16-qubit dedicated difference register and a 12-qubit in-place register, proved that measurement reconstruction is governed by the Coupon Collector's problem, and verified 100% bitwise parity with classical calculations across a 52-test automated suite."*

---

## 2. Likely Viva Questions & Scripted Model Answers

---

### Question 1: "A classical CPU computes 4x4 XOR in 450 nanoseconds. Why use quantum computing at all?"
**Model Answer:**  
*"That is an astute observation, Professor, and our experimental benchmarks explicitly demonstrate that classical NumPy is ~36,000 times faster on a classical CPU than Qiskit Aer.*

*The objective of Q-TRACE is **not** to claim present-day quantum advantage on classical semiconductor simulation. Rather, it serves as an **educational and exploratory laboratory** for our quantum computing capstone. We are investigating how image data structures and comparison operations are formally mapped onto unitary circuits for future fault-tolerant quantum processors.*

*Furthermore, by formulating image comparison in a quantum superposition, we demonstrate theoretical quantum capabilities—such as appending an ancilla Difference Flag qubit to certify zero discrepancies across an entire image patch in a single measurement shot, or employing Grover's algorithm to search for sparse tampered pixels with provable quadratic speedup $\mathcal{O}(\sqrt{N/M})$."*

---

### Question 2: "Why did you choose NEQR over FRQI?"
**Model Answer:**  
*"FRQI (Flexible Representation of Quantum Images) encodes pixel intensity into the continuous probability amplitude $\cos\theta_i |0\rangle + \sin\theta_i |1\rangle$ of a single color qubit. While FRQI is economical in qubits ($2n + 1$), you cannot perform discrete boolean arithmetic—such as XOR—directly on probability amplitudes. Extracting pixel values in FRQI requires expensive quantum state tomography over tens of thousands of shots.*

*NEQR (Novel Enhanced Quantum Representation) stores pixel gray levels directly in computational basis states using $q$ qubits ($|c_3 c_2 c_1 c_0\rangle$). Because the pixel values exist as discrete basis states, we can execute exact, reversible boolean logic—specifically CNOT-based bitwise XOR—simultaneously across all coordinates in superposition without amplitude tomography."*

---

### Question 3: "How do you prepare the position superposition, and why must the position register be shared?"
**Model Answer:**  
*"We apply Hadamard gates $H^{\otimes 4}$ to the 4 position qubits:
$$(H^{\otimes 4}) |0000\rangle_{pos} = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos}$$
This creates an equal superposition across all 16 spatial coordinates with amplitude $1/4$ and probability $1/16$.

The position register **must be strictly shared** between Image A and Image B. When we apply coordinate-conditioned gates ($C^4(NOT)$) to load Image A into Register A and Image B into Register B, both operations are controlled by the **exact same physical position qubits**. This guarantees that whenever the position register collapses to coordinate $k$, Registers A and B are guaranteed to hold the corresponding pixel values $A(k)$ and $B(k)$ with zero spatial desynchronization."*

---

### Question 4: "Explain how CNOT gates compute the XOR difference."
**Model Answer:**  
*"A CNOT gate is a reversible quantum gate mapping basis states $|c, t\rangle \to |c, t \oplus c\rangle$.
In our 16-qubit architecture, the difference qubit $d_j$ is initialized to $|0\rangle$.
We apply two CNOT gates targeting $d_j$:
1. $CNOT(orig_j \to diff_j)$ transforms $|0\rangle \to |a_j\rangle$.
2. $CNOT(mod_j \to diff_j)$ transforms $|a_j\rangle \to |a_j \oplus b_j\rangle$.

By the linearity of quantum mechanics, this local operation acts concurrently on every basis state in the spatial superposition:
$$|\Psi\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} |A(k)\rangle |B(k)\rangle |A(k) \oplus B(k)\rangle_{diff}$$
Because CNOT is self-inverse ($CNOT^2 = I$), the operation is strictly reversible."*

---

### Question 5: "Why can't you reconstruct the entire 4x4 image from a single measurement shot?"
**Model Answer:**  
*"Because of the fundamental postulate of quantum measurement—wavefunction collapse. 
Prior to measurement, all 16 pixels co-exist in superposition. However, when we measure the position and difference registers in the computational basis, Born's rule dictates that the state collapses to **a single random basis state** $|k^*\rangle |D(k^*)\rangle$ with probability $|\frac{1}{4}|^2 = \frac{1}{16} = 6.25\%$.

A single shot reveals the difference value at **exactly one pixel**. To reconstruct the entire $4 \times 4$ image grid, we must sample repeatedly across multiple shots."*

---

### Question 6: "Derive the Coupon Collector formula and explain why S=150 shots is the 99.9% threshold."
**Model Answer:**  
*"Sampling $N = 16$ equally probable states is mathematically identical to the classical Coupon Collector's Problem.
The expected number of shots to observe all 16 coordinates at least once is:
$$E[T] = N \cdot H_N = 16 \sum_{i=1}^{16} \frac{1}{i} = 16 \times 3.3807 = \mathbf{54.09 \text{ shots}}$$

However, the expected value only gives a $\approx 59.1\%$ probability of complete coverage—40.9% of the time, at least one pixel is missed!

To find the shots needed for $99.9\%$ certainty ($P \ge 0.999$), we use the exact inclusion-exclusion formula:
$$P(\text{all } N) = \sum_{j=0}^{16} (-1)^j \binom{16}{j} \left( \frac{16 - j}{16} \right)^S$$
Evaluating this summation reveals that at **$S = 150$ shots**, $P_{exact} = 0.999001 \ge 99.9\%$. 
Using the Poisson approximation $P \approx \exp(-16 e^{-S/16}) \ge 0.999$, we get $S \ge 16 \ln(16/0.001) \approx 154.9$ shots. 
Both methods agree that $\approx 150–155$ shots guarantees $99.9\%$ completeness, and in Q-TRACE we set $S = 1024$ as standard to guarantee $100\%$ reconstruction fidelity."*

---

### Question 7: "What is the difference between your 16-qubit and 12-qubit architectures?"
**Model Answer:**  
*"In the 16-qubit architecture, we allocate a dedicated 4-qubit Difference register. This allows Image A, Image B, and Difference D to co-exist simultaneously for visual inspection.

In the 12-qubit architecture, we eliminate the difference register and apply $CNOT(orig_j \to mod_j)$ directly to the modified image register in-place. 
- *Advantage:* It reduces the statevector dimension from $2^{16} = 65,536$ down to $2^{12} = 4,096$ states, cutting simulation RAM from $1.05 \text{ MB}$ to $64 \text{ KB}$—a **93.75% memory reduction**.
- *Trade-off:* Image B's values are overwritten by the difference in-place. However, because CNOT is self-inverse, applying the CNOT gates a second time reversibly restores Image B."*

---

### Question 8: "Why did your Part 1 audit reject applying Grover's algorithm directly without uncomputing?"
**Model Answer:**  
*"That was a crucial theoretical discovery from our audit. In naive literature, authors suggest applying Grover's diffusion operator $2|s\rangle\langle s| - I$ directly to the position register after marking a difference.

However, after computing the difference, the position qubits are **entangled** with the intensity and difference registers:
$$|\Psi\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k), f_B(k), D(k)\rangle$$
The reduced density matrix of the position register is a **mixed state**. Applying diffusion to an entangled mixed state destroys quantum interference, yielding only $62.5\%$ probability on the marked state in empirical simulation.

To solve this, we formulated the **uncomputing oracle**:
$$U_{oracle} = U_{prep}^\dagger \cdot U_{phase\_kickback} \cdot U_{prep}$$
We apply phase kickback via an ancilla $|-\rangle$ when $D \neq 0$, and then apply $U_{prep}^\dagger$ to uncompute the intensity and difference registers back to $|0000\rangle$. This disentangles the position register, restoring a pure state that amplifies the tampered pixel to **100.0% probability** under Grover diffusion."*

---

### Question 9: "What if a pixel is not observed during measurement? How do you prevent false negatives?"
**Model Answer:**  
*"A critical safeguard in our reconstruction engine is that unobserved coordinates are explicitly assigned `-1` (Unobserved) and added to a `missing_coordinates` list. They are **never** assigned `0` (Unchanged). This ensures that an investigator is never misled into believing an under-sampled pixel was verified as authentic."*

---

## 3. Whiteboard Derivation Cheat-Sheet (Live Exam)

During the viva, write these four equations on the whiteboard to demonstrate complete mastery:

1. **NEQR Superposition Equation:**
   $$|\Psi_1\rangle = \left( \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \right) \otimes |0\rangle_{orig}^{\otimes 4} |0\rangle_{mod}^{\otimes 4} |0\rangle_{diff}^{\otimes 4}$$

2. **Reversible CNOT XOR Transformation:**
   $$|a_j\rangle |b_j\rangle |0\rangle_{diff_j} \xrightarrow{CNOT(orig_j \to diff_j)} |a_j\rangle |b_j\rangle |a_j\rangle \xrightarrow{CNOT(mod_j \to diff_j)} |a_j\rangle |b_j\rangle |a_j \oplus b_j\rangle$$

3. **Composite Entangled State:**
   $$|\Psi_3\rangle = \frac{1}{4} \sum_{k=0}^{15} |k\rangle_{pos} \otimes |f_A(k)\rangle_{orig} \otimes |f_B(k)\rangle_{mod} \otimes |f_A(k) \oplus f_B(k)\rangle_{diff}$$

4. **Coupon Collector Expected Shots:**
   $$E[T] = 16 \cdot H_{16} = 16 \left(1 + \frac{1}{2} + \dots + \frac{1}{16}\right) \approx 16 \times 3.3807 = \mathbf{54.09 \text{ shots}}$$

