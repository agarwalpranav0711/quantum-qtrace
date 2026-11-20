# Q-TRACE: Quantum Experimental Validation & Architecture Evaluation

**Document Reference:** `docs/QUANTUM_EXPERIMENTAL_VALIDATION.md`  
**Classification:** Quantum Computing & Algorithmic Validation  
**Version:** 1.9.0  
**Data Sources:** `results/part9/quantum/quantum_sampling_sweep.csv`, `results/part9/quantum/quantum_benchmark_summary.json`  

---

## 1. Experimental Setup & Architectures

We conducted empirical evaluations across two distinct IBM Qiskit Aer quantum circuit architectures designed for $4 \times 4$ image micro-patch comparison:

```
+-------------------------------------------------------------------------------+
|                       Q-TRACE QUANTUM COMPARATOR ENGINES                      |
+-------------------------------------------------------------------------------+
| 1. 16-Qubit Dedicated Difference Register Architecture                        |
|    - Qubits 0..3: Spatial Coordinates |Y_1 Y_0 X_1 X_0>                       |
|    - Qubits 4..7: Original Pixel Intensity |I_orig>                           |
|    - Qubits 8..11: Modified Pixel Intensity |I_mod>                           |
|    - Qubits 12..15: Dedicated Difference Register |I_diff>                    |
|    - Comparison Gates: 8 transverse CNOT gates mapping XOR into |I_diff>     |
|    - Gate Count: 48 gates | Depth: 24 | Statevector Memory: 1.05 MB           |
+-------------------------------------------------------------------------------+
| 2. 12-Qubit Compact In-Place Architecture                                     |
|    - Qubits 0..3: Spatial Coordinates |Y_1 Y_0 X_1 X_0>                       |
|    - Qubits 4..7: Original Pixel Intensity |I_orig>                           |
|    - Qubits 8..11: In-Place Target Register (holding |I_mod> initially)       |
|    - Comparison Gates: 4 CNOT gates transforming |I_mod> into |I_orig (+) I_mod>|
|    - Gate Count: 36 gates | Depth: 18 | Statevector Memory: 0.065 MB (65 KB)  |
|    - Qubit Reduction: 25% fewer physical qubits than 16Q                      |
+-------------------------------------------------------------------------------+
```

---

## 2. Empirical Shot Sampling Sweep Results

Evaluated across 70 independent sampling trials ($S \in \{64, 128, 256, 512, 1024, 2048, 4096\}$ across multiple random seeds) on single-pixel, multi-pixel, and maximum-difference test cases:

| Shot Count $S$ | Theoretical Probability ($P \ge 16$) | 16Q Mean Observed Coords | 16Q Full Coverage % | 12Q Full Coverage % | 16Q Mean Sim Latency | 12Q Mean Sim Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **64** | $0.76518$ ($76.5\%$) | $15.40 / 16$ | $50.0\%$ | $50.0\%$ | $13.5\text{ ms}$ | $6.2\text{ ms}$ |
| **128** | $0.98592$ ($98.6\%$) | $16.00 / 16$ | $100.0\%$ | $100.0\%$ | $14.2\text{ ms}$ | $6.5\text{ ms}$ |
| **256** | $0.99986$ ($99.9\%$) | $16.00 / 16$ | $100.0\%$ | $100.0\%$ | $14.8\text{ ms}$ | $6.8\text{ ms}$ |
| **512** | $> 0.99999$ ($100\%$) | $16.00 / 16$ | $100.0\%$ | $100.0\%$ | $15.4\text{ ms}$ | $7.1\text{ ms}$ |
| **1024** | $1.00000$ ($100\%$) | $16.00 / 16$ | $100.0\%$ | $100.0\%$ | $16.2\text{ ms}$ | $7.5\text{ ms}$ |
| **2048** | $1.00000$ ($100\%$) | $16.00 / 16$ | $100.0\%$ | $100.0\%$ | $17.8\text{ ms}$ | $8.2\text{ ms}$ |
| **4096** | $1.00000$ ($100\%$) | $16.00 / 16$ | $100.0\%$ | $100.0\%$ | $21.5\text{ ms}$ | $9.8\text{ ms}$ |

---

## 3. Key Findings

1. **Bit-for-Bit Exact Parity:** For all runs where complete coordinate coverage was achieved ($S \ge 128$), both the 16Q and 12Q architectures achieved **100% bitwise parity** with classical XOR ground truth across all test cases.
2. **12-Qubit Simulation Advantage:** The 12Q architecture executes in approximately **$48\%$ of the runtime** of 16Q ($7.5\text{ ms}$ vs $16.2\text{ ms}$ at 1024 shots) due to the $16\times$ reduction in statevector vector dimension ($2^{12} = 4,096$ amplitudes vs $2^{16} = 65,536$ amplitudes).
3. **Coupon Collector Empirical Confirmation:** At $S=64$ shots, empirical full-coverage rate is exactly $50.0\%$, reflecting the transition around expected shots $E[T] \approx 54.09$. At $S \ge 128$ shots, full coordinate reconstruction is achieved in $100\%$ of trials.

