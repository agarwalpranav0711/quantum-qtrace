# Q-TRACE: Quantum Resource Scaling & Simulation Memory Limits

**Document Reference:** `docs/QUANTUM_RESOURCE_SCALING.md`  
**Classification:** Quantum Complexity Theory & Hardware Requirements  
**Version:** 1.9.0  

---

## 1. Mathematical Scaling of Statevector Simulation

Simulating a quantum register of $n$ qubits on classical hardware requires storing the complete statevector consisting of $2^n$ complex amplitudes.

Using double-precision complex numbers (`complex128`), each complex amplitude consumes 16 bytes (8 bytes for the real component, 8 bytes for the imaginary component):

$$\text{Memory (bytes)} = 16 \times 2^n$$

---

## 2. Resource Scaling Across Image Dimensions

| Image Dimensions | Total Pixels | Qubit Allocation ($2 \times \text{Coords} + 2 \times \text{Intensities} + \text{Diff}$) | Total Qubits ($n$) | Statevector Memory Required | Classical Simulation Feasibility |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$4 \times 4$ (Micro-patch)** | 16 | $4\text{ pos} + 4\text{ orig} + 4\text{ mod} + 4\text{ diff}$ | **16 qubits** | **$1.05\text{ MB}$** | **Feasible in real-time** ($< 100\text{ ms}$) |
| **$4 \times 4$ (In-place 12Q)**| 16 | $4\text{ pos} + 4\text{ orig} + 4\text{ in-place}$ | **12 qubits** | **$65.5\text{ KB}$** | **Instantaneous** ($< 10\text{ ms}$) |
| **$8 \times 8$ Patch** | 64 | $6\text{ pos} + 8\text{ orig} + 8\text{ mod} + 8\text{ diff}$ | **30 qubits** | **$17.18\text{ GB}$** | Feasible only on high-end server RAM |
| **$16 \times 16$ Tile** | 256 | $8\text{ pos} + 8\text{ orig} + 8\text{ mod} + 8\text{ diff}$ | **32 qubits** | **$68.72\text{ GB}$** | Exceeds standard workstation RAM |
| **$32 \times 32$ Thumbnail**| 1,024 | $10\text{ pos} + 8\text{ orig} + 8\text{ mod} + 8\text{ diff}$ | **34 qubits** | **$274.88\text{ GB}$** | Requires HPC cluster |
| **$256 \times 256$ Image** | 65,536 | $16\text{ pos} + 8\text{ orig} + 8\text{ mod} + 8\text{ diff}$ | **40 qubits** | **$17.59\text{ TB}$** | Top supercomputer tier |
| **$1024 \times 1024$ Full HD**| 1,048,576 | $20\text{ pos} + 8\text{ orig} + 8\text{ mod} + 8\text{ diff}$ | **44 qubits** | **$281.47\text{ TB}$** | Globally impossible to classically simulate |

---

## 3. Justification for Q-TRACE's $4 \times 4$ Architectural Boundary

The resource scaling table demonstrates why Q-TRACE strictly restricts quantum simulation to investigator-targeted **$4 \times 4$ micro-patches**:
1. At 16 qubits, memory consumption is capped at $1.05\text{ MB}$, allowing flawless, crash-free execution on any examiner's local laptop.
2. Simulating even an $8 \times 8$ patch with 8-bit color would require $17.18\text{ GB}$ of dedicated RAM, causing out-of-memory crashes on consumer devices.
3. Claims by competing prototypes to simulate full megapixel quantum images on laptops are mathematically impossible and indicate either hidden classical mocking or severe misunderstanding of quantum statevector scaling.

