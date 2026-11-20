# Q-TRACE Forensic Test Image Dataset & Ground Truth Guide

**Location:** `d:\WebDev PROJECTS\quantum qtrace\test_samples\`

---

## 1. Test Files Overview

### File 1: `real_car_claim.jpg` (Pristine Reference Baseline)
- **Status:** **REAL / AUTHENTIC**
- **Dimensions:** $800 \times 600$ pixels
- **Compression:** Single-pass authentic JPEG ($Q = 92$)
- **Noise Characteristics:** Continuous Gaussian photon sensor pattern noise ($\sigma \approx 4.0$) across all vehicle panels and body contours.
- **SHA-256 Digest:** `80801C7884C5E14F67061E1125947ADA930936783C70667A0F7B6EE8C4AC378E`

---

### File 2: `fake_tampered_claim.jpg` (Manipulated Evidence)
- **Status:** **FAKE / TAMPERED**
- **Dimensions:** $800 \times 600$ pixels
- **Compression:** Multi-pass secondary recompression ($Q = 75$)
- **SHA-256 Digest:** `3A04AD613E1E031E21151509B90EAFE12A730FF7352B3FEBD6123782A9E882D8`

#### Specific Tampering Injected:
1. **Copy-Move Duplication (Clone-Stamping):**
   - **Source Region ($A$):** Coordinates $[X: 120-200, Y: 250-310]$ (scratch contour).
   - **Cloned Target Region ($B$):** Coordinates $[X: 380-460, Y: 270-330]$.
   - *Expected Detection:* The SIFT/ORB Copy-Move detector will match feature descriptors between regions $A$ and $B$ and draw connection vectors.
2. **Spliced Foreign Damage Insert:**
   - **Spliced Bounding Box:** Coordinates $[X: 200-320, Y: 380-480]$ (cracked bumper seam).
   - **Mismatches:** Inserted with severe foreign noise ($\sigma = 16.0$) and high-pass frequency disparity.
   - *Expected Detection:*
     - **Error Level Analysis (ELA):** Shows bright compression error residuals on the perimeter $[X: 200-320, Y: 380-480]$.
     - **Noise Variance:** Highlights an anomalous outlier tile ($> 3.0 \times \text{MAD}$).
3. **Quantum Micro-Patch Comparison:**
   - Comparing a $4 \times 4$ micro-patch from the spliced seam against the pristine baseline will produce **Uhlmann Quantum Fidelity $F < 0.88$** and high Trace Distance ($D > 0.35$).
   - Comparing two pristine regions will produce **Uhlmann Quantum Fidelity $F > 0.995$**.

