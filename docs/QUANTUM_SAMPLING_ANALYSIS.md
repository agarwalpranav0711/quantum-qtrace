# Q-TRACE: Quantum Sampling & Coupon Collector Theoretical Verification

**Document Reference:** `docs/QUANTUM_SAMPLING_ANALYSIS.md`  
**Classification:** Quantum Measurement Theory & Mathematical Proofs  
**Version:** 1.9.0  

---

## 1. The Coupon Collector Problem in Quantum Forensics

In Quantum Image Processing (QIP) using Novel Enhanced Quantum Representation (NEQR), an image is prepared as an equal superposition over all spatial coordinates $(y, x)$:

$$|\Psi\rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} |k\rangle |I(k)\rangle$$

When measuring this state to reconstruct the underlying pixel values, each shot randomly collapses the wavefunction into one specific coordinate basis state $|k\rangle$.

Reconstructing the complete $N$-pixel difference image requires collecting at least one measurement for each of the $N$ distinct coordinates. This is mathematically isomorphic to the classical **Coupon Collector Problem**.

---

## 2. Mathematical Derivation of Sampling Bounds

For an image patch of size $4 \times 4$ ($N = 16$ coordinates):

### 2.1 Expected Shot Count
Let $T$ be the number of shots required to observe all 16 coordinates. The expected value is:

$$E[T] = N \sum_{i=1}^{N} \frac{1}{i} = 16 \left( 1 + \frac{1}{2} + \frac{1}{3} + \dots + \frac{1}{16} \right) = 16 \times 3.3807 \approx \mathbf{54.09\text{ shots}}$$

### 2.2 Exact Probability of Complete Coverage
Using the principle of inclusion-exclusion, the exact probability that all $N$ coordinates have been observed after $s$ shots is:

$$P(T \le s) = \sum_{j=0}^{N} (-1)^j \binom{N}{j} \left( 1 - \frac{j}{N} \right)^s$$

For $N = 16$:
- At $s = 64$ shots: $P(T \le 64) \approx 0.76518$ ($76.5\%$)
- At $s = 128$ shots: $P(T \le 128) \approx 0.98592$ ($98.6\%$)
- At $s = 155$ shots: $P(T \le 155) \ge 0.99900$ ($99.9\%$)
- At $s = 1024$ shots: $P(T \le 1024) = 1.00000$ ($100.0\%$)

### 2.3 Tail Bound & Poisson Approximation
The probability that at least one coordinate remains unobserved after $s$ shots is bounded by:

$$P(T > s) \le N \left( 1 - \frac{1}{N} \right)^s \le N e^{-s/N}$$

Setting the failure probability $\delta = 0.001$ ($99.9\%$ confidence):

$$16 e^{-s/16} \le 0.001 \implies e^{s/16} \ge 16,000 \implies s \ge 16 \ln(16,000) \approx 16 \times 9.68 \approx 154.9\text{ shots}$$

Hence, **a minimum of 155 shots guarantees with $99.9\%$ theoretical certainty that every pixel in a $4 \times 4$ patch is observed.**

---

## 3. Incomplete Readout Handling: The -1 Protocol

When an examiner runs a quantum experiment with low shot counts (e.g. $S = 32$), certain coordinates will have zero observations.

In naive implementations, unobserved pixels are frequently initialized to $0$, creating a severe forensic vulnerability: **an unobserved pixel is misclassified as zero difference (authentic), hiding potential tampering.**

Q-TRACE strictly enforces the **Incomplete Reconstruction Protocol**:
- Unobserved pixels are explicitly assigned a value of `-1` (or `NaN`).
- Visual heatmaps render unobserved coordinates as a diagonal hatching pattern labeled *"Unobserved / Insufficient Quantum Sampling"*.
- The difference metrics calculation partitions results into `observed_pixel_count` and `missing_coordinates`.

