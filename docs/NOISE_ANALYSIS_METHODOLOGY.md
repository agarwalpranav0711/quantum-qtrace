# Q-TRACE Sensor Noise Inconsistency Methodology

**Document ID:** `DOC-MET-002`  
**Classification:** Sensor Physics & Signal Analysis Methodology  
**Version:** 1.0.0 (Part 5 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Forensics Engineering Team

---

## 1. Physical Principles of Camera Sensor Noise

Every digital camera sensor (CMOS or CCD) imprints a unique, stochastic high-frequency noise fingerprint upon raw radiance during photo capture:
$$I(x, y) = I_0(x, y) + I_0(x, y) \cdot K(x, y) + \Theta(x, y)$$

where:
- $I_0(x, y)$ is the incident noise-free scene radiance.
- $K(x, y)$ is the **Photo-Response Non-Uniformity (PRNU)**—a deterministic sensor fingerprint caused by microscopic silicon pixel variations during wafer fabrication.
- $\Theta(x, y)$ represents zero-mean stochastic noise (photon shot noise, dark current, and read noise) characterized by a local variance $\sigma^2_N$.

When a fraudster splices a dent or scratch from an external photograph (captured with a different camera model or downloaded from an online image search) onto a vehicle claim photograph, the **noise variance of the foreign patch rarely matches the host camera sensor's noise floor**.

---

## 2. High-Frequency Noise Residual Extraction

Q-TRACE isolates high-frequency residuals by estimating the underlying clean scene radiance $\hat{I}_0(x, y)$ using a $3 \times 3$ adaptive median filter:

$$\hat{I}_0(x, y) = \operatorname{MedianFilter}_{3 \times 3}(I(x, y))$$
$$\hat{N}(x, y) = |I(x, y) - \hat{I}_0(x, y)|$$

The absolute residual $\hat{N}(x, y)$ removes low-frequency scene edges while preserving high-frequency sensor noise and micro-texture variations.

---

## 3. Block-Level Variance & Non-Linear Exposure Masking

### 3.1 Spatial Variance Estimation
The image is segmented into uniform spatial blocks $B_k$ of size $W \times W$ ($W = 16 \text{ or } 32$ pixels). For each block:
$$\sigma^2(B_k) = \frac{1}{W^2} \sum_{(x, y) \in B_k} (\hat{N}(x, y) - \mu_{B_k})^2$$

### 3.2 Non-Linear Saturation Masking
Sensor noise behavior is inherently non-linear at extreme exposures:
- **Deep Shadows** ($I < 15$): Sensor noise is clipped by quantization and dark-current floor.
- **Saturated Highlights** ($I > 240$): Photon well capacity is full; variance collapses to near zero.

To prevent false alarms in deep wheel-well shadows or chrome reflections, Q-TRACE masks blocks whose mean intensity falls outside $[15, 240]$:
$$M_{valid}(B_k) = \mathbb{I}(15 \le \mu_I(B_k) \le 240)$$

---

## 4. Anomaly Thresholding & Visual Artifact Rendering

1. **Baseline Parameter Estimation**:
   Compute the robust global median noise variance $\bar{\sigma}^2$ and standard deviation $\sigma_{\sigma^2}$ across all valid blocks.
2. **Discrepancy Identification**:
   A block is flagged if its local noise variance departs significantly from the sensor baseline:
   $$|\sigma^2(B_k) - \bar{\sigma}^2| > \tau_{noise} \cdot \sigma_{\sigma^2} \quad (\tau_{noise} = 2.8)$$
3. **Artifact Generation (`NOISE_HEATMAP`)**:
   The variance matrix is normalized to $[0, 255]$, resized to full resolution using nearest-neighbor interpolation, colorized with the **JET colormap**, and alpha-blended (45% heatmap, 55% original evidence) to give the examiner precise anatomical context on the vehicle.
4. **RoI & Quantum Patch Extraction**:
   Contiguous components of anomalous blocks are bounded into candidate RoIs, and the centroid $4 \times 4$ patch is quantized down to $[0, 15]$ for algebraic verification.

