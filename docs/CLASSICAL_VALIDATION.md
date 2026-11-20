# Q-TRACE — Classical Validation & Equivalence Verification

**Document ID:** `DOC-VAL-001`  
**Classification:** Verification & Validation Specification  
**Version:** 1.0.0 (Part 2 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Quantum Engineering Team  
**Scope:** Independent Verification Methodology, Equivalence Proofs, and Test Coverage  

---

## 1. Principles of Independent Verification

A core tenet of scientific software engineering in Q-TRACE is that **quantum computation must never validate itself**. 

To prevent circular reasoning or confirmation bias:
1. The **Classical Comparator** (`src/classical/comparator.py`) was developed completely independently of any quantum library, using standard NumPy vector operations.
2. The expected difference maps for all test cases were computed deterministically via CPU bitwise logic *prior* to circuit construction.
3. Quantum simulation outputs from `src/quantum/reconstruction.py` were checked against classical outputs using strict assertion equivalence:
   $$\forall (r, c) \in \{0..3\} \times \{0..3\}: \quad D_{quantum}(r, c) \equiv D_{classical}(r, c)$$

---

## 2. Independent Classical Formulation

For two 4x4 4-bit grayscale matrices $A, B \in \{0..15\}^{4 \times 4}$:

### 2.1 Bitwise XOR Difference:
$$D_{XOR}(y, x) = A(y, x) \oplus B(y, x)$$
- Identical pixels yield $D_{XOR} = 0$.
- Different pixels yield non-zero integers in $[1, 15]$.

### 2.2 Absolute Intensity Difference:
$$D_{abs}(y, x) = |A(y, x) - B(y, x)|$$
- Measures the scalar magnitude of modification in $[0, 15]$.

### 2.3 Threshold-Based Tamper Mask:
$$M(y, x) = \begin{cases} 1 & \text{if } D_{XOR}(y, x) > 0 \\ 0 & \text{otherwise} \end{cases}$$

---

## 3. Handling Unobserved Coordinates: The Non-Zero Bias Safeguard

A major failure mode in naive quantum image sampling is treating missing/unobserved coordinates as "zero" (unchanged).

In Q-TRACE:
- If a coordinate $(r, c)$ receives zero measurement counts during an under-sampled run ($S < 150$), it is explicitly assigned `-1` (Unobserved) in `reconstructed_diff`.
- It is appended to `missing_coordinates` and flagged with `is_observed = False`.
- In automated testing (`test_unobserved_pixels_never_classified_as_zero` in `tests/test_reconstruction.py`), this safeguard is verified to prevent unobserved pixels from ever being reported as authentic or unchanged.

---

## 4. The 52-Test Automated Pytest Suite

The automated test suite verifies 52 distinct properties across unit and integration levels:

```
Test Module                      | Tests Passed | Core Properties Validated
---------------------------------+--------------+-------------------------------------------------------------
tests/test_classical.py          | 7            | Shape validation, range bounds, XOR logic, metrics dict
tests/test_quantum_state_prep.py | 4            | Coordinate roundtrip, H superposition, uncomputing reversibility
tests/test_quantum_16q.py        | 7            | 16Q circuit builder, resources, identical, single, multi, max
tests/test_quantum_12q.py        | 5            | 12Q circuit builder, in-place XOR, in-place reversibility
tests/test_reconstruction.py     | 7            | Bitstring decoding, unobserved coordinates, Coupon Collector math
tests/test_end_to_end.py         | 22           | Parametric equivalence across 8 test cases & 5 random seeds
---------------------------------+--------------+-------------------------------------------------------------
TOTAL                            | 52 / 52      | 100% Pass Rate (3.21 seconds execution time)
```

### Key Integration Test Cases:
- **`test_16q_single_pixel_change`:** Tests pixel $(1, 2)$ changing from $7 \to 12$. Confirms output pixel is strictly $11$, and all remaining 15 pixels are strictly $0$.
- **`test_16q_identical_images`:** Tests two identical gradient images. Confirms all 16 difference values are strictly $0$.
- **`test_12q_in_place_reversibility`:** Executes circuit with `uncompute_diff=True`. Verifies that the second CNOT pass restores Image B in the target register with 100% fidelity.
- **`test_end_to_end_random_trials`:** Generates random image pairs across 5 distinct seeds, confirming bitwise equivalence in every trial.

---

*Continue to `RESOURCE_ANALYSIS.md` for gate counts, circuit depths, memory scaling formulas, and CPU runtime benchmarks.*

