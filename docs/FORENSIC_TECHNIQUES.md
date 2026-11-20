# Q-TRACE Classical Forensic Techniques Reference Catalog

**Document ID:** `DOC-CAT-005`  
**Classification:** Algorithmic & Methodological Catalog  
**Version:** 1.0.0 (Part 5 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Forensics Engineering Team

---

## 1. Catalog Summary

The Q-TRACE classical engine provides 7 orthogonal forensic techniques covering container metadata, frequency compression, sensor hardware noise, spatial cloning, statistical signal distribution, perceptual identity, and boundary continuity.

| ID | Technique Name | Version | Category | Primary Target Forgery | Artifact Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`metadata`** | Image Metadata & EXIF Integrity | 1.0.0 | Container & Provenance | Editing tool traces, timestamp fraud | Structured JSON |
| **`ela`** | Error Level Analysis (ELA) | 1.0.0 | Compression Physics | JPEG splices, inserted digital graphics | `ELA_HEATMAP` |
| **`noise`** | Sensor Noise Inconsistency | 1.0.0 | Sensor Physics | Foreign sensor patches, smooth retouches | `NOISE_HEATMAP` |
| **`copy_move`**| Copy-Move Forgery (CMFD) | 1.0.0 | Geometric & Spatial | Cloned damage (dents, scratches, rust) | `CMFD_MATCHES` |
| **`statistics`**| Statistics & Histograms | 1.0.0 | Signal Distribution | Tonal adjustment, clipping, comb gaps | `HISTOGRAM_PLOT` |
| **`perceptual_hash`**| Perceptual Hashing (a/d/pHash)| 1.0.0 | Fingerprinting & Identity | Duplicate claims, resized re-submissions | Hash Matrix |
| **`resampling`**| Edge Gradient & Inpainting | 1.0.0 | Edge & Interpolation | Erased scratches, boundary feathering | `EDGE_GRADIENT_MAP`|

---

## 2. Technique Specifications

### 2.1 Image Metadata & EXIF Integrity (`metadata`)
- **What It Measures**: Structural container headers, EXIF tags, camera hardware metadata (Make, Model, Lens), embedded timestamps (`DateTimeOriginal`, `DateTimeDigitized`, `DateTime`), software signatures, orientation, and C2PA provenance containers.
- **Algorithm**: Decodes EXIF dictionary using Pillow `_getexif()` and `ExifTags.TAGS`. Sanitizes binary data. Evaluates `Software` and `ProcessingSoftware` against known image-manipulation suites (Photoshop, GIMP, Canva, Snapseed, Lightroom, VSCO, Inpaint).
- **Parameters**: None.
- **Artifacts**: Machine-readable metadata metrics and timestamps.
- **Insurance Relevance**: High. Novice fraudsters frequently save edited vehicle photos from Photoshop or Canva without stripping software tags; exposes post-capture modification.
- **Limitations**: EXIF can be trivially stripped or spoofed; absence is not proof of tampering.

---

### 2.2 Error Level Analysis (`ela`)
- **What It Measures**: Rate-distortion compression delta by re-compressing the image at a known reference JPEG quality grid (default: 95) and computing absolute pixel differences.
- **Mathematical Formulation**:
  $$E(x, y) = |I_{orig}(x, y) - I_{resave}(x, y)|$$
  $$\operatorname{ELA}(x, y) = \min(255, \alpha \cdot E(x, y))$$
- **Edge-Masking Enhancement**: Natural high-contrast boundaries (e.g. car door seams, chrome rims) have high DCT high-frequency residuals. Q-TRACE computes Sobel edge gradients and masks out the top 15% edge magnitudes before clustering anomalous blocks.
- **Parameters**: `quality` (50–100, default 95), `scale` (5–30, default 15), `edge_masking` (bool, default True), `roi_threshold_std` (float, default 2.5).
- **Artifacts**: Enhanced ELA visualization (`ELA_HEATMAP`, PNG).
- **Insurance Relevance**: High. Detects digital stickers, spliced license plates, or foreign damage patches added to pre-loss photos.
- **Limitations**: Repeated global re-saving elevates the overall error floor. Non-JPEG images simulate first-generation JPEG encoding.

---

### 2.3 Sensor Noise Inconsistency Analysis (`noise`)
- **What It Measures**: Spatial distribution and consistency of high-frequency camera sensor noise residuals (PRNU and shot noise).
- **Mathematical Formulation**:
  $$\hat{I}_0(x, y) = \operatorname{MedianFilter}_{k \times k}(I(x, y))$$
  $$\hat{N}(x, y) = |I(x, y) - \hat{I}_0(x, y)|$$
  $$\sigma^2(B_k) = \frac{1}{|B_k|} \sum_{(x, y) \in B_k} (\hat{N}(x, y) - \mu_{B_k})^2$$
  Blocks where $|\sigma^2(B_k) - \bar{\sigma}^2| > \theta \cdot \sigma_{\sigma^2}$ are flagged.
- **Parameters**: `block_size` (16 or 32 px, default 16), `filter_kernel` (3 or 5, default 3), `variance_threshold_sigma` (float, default 2.8).
- **Artifacts**: Continuous 2D noise variance heatmap blended with the original evidence (`NOISE_HEATMAP`, PNG).
- **Insurance Relevance**: High. Catches uncompressed or raw image splices where noise floor does not match the host camera sensor.
- **Limitations**: Saturated highlights (pure white) and underexposed shadows (pure black) naturally suppress noise.

---

### 2.4 Copy-Move Forgery Detection (`copy_move`)
- **What It Measures**: Spatial duplication of identical or affine-transformed patches across the image (cloned damage insertion).
- **Algorithm**:
  1. Extract SIFT scale- and rotation-invariant keypoints (or ORB binary descriptors).
  2. Compute 4-NN feature descriptor matches.
  3. Apply Lowe's ratio test: $\frac{d_1}{d_2} < \tau_{ratio}$ (default 0.68).
  4. Enforce minimum spatial distance: $\|\mathbf{x}_i - \mathbf{x}_j\|_2 \ge d_{min}$ (default 35 px) to eliminate self-matches.
  5. Cluster parallel displacement vectors $(\Delta x, \Delta y)$ within distance and angle tolerances.
  6. Compute bounding boxes around source and target clusters.
- **Parameters**: `algorithm` ("SIFT" or "ORB"), `ratio_threshold` (0.50–0.80), `min_spatial_distance` (float), `min_cluster_size` (int).
- **Artifacts**: Keypoint vector connection overlay (`CMFD_MATCHES`, PNG).
- **Insurance Relevance**: Critical. Identifies cloned dents, duplicated body scratches, or stamped texture used to inflate repair estimates.
- **Limitations**: Fails on smooth textureless surfaces (polished car panels); repetitive physical structures (grilles, wheels) can cause false positives.

---

### 2.5 Image Statistics & Multi-Channel Histograms (`statistics`)
- **What It Measures**: 256-bin channel histograms (Red, Green, Blue, Luminance), Shannon information entropy, dispersion (skewness, kurtosis), dynamic range, and pixel clipping.
- **Mathematical Formulation**:
  $$H = -\sum_{i=0}^{255} p(i) \log_2 p(i)$$
  $$\text{Clipping} = \frac{\#\{I=0\} + \#\{I=255\}}{W \times H} \times 100\%$$
- **Parameters**: `clipping_threshold_percent` (float, default 5.0%), `comb_anomaly_threshold` (int, default 8 gaps).
- **Artifacts**: Multi-channel RGB and Luminance distribution plot (`HISTOGRAM_PLOT`, PNG).
- **Insurance Relevance**: Medium. Exposes aggressive contrast adjustment, histogram equalization, and harsh digital editing.

---

### 2.6 Perceptual Hashing & Similarity (`perceptual_hash`)
- **What It Measures**: 64-bit visual perceptual hashes (aHash, dHash, DCT-based pHash) invariant to compression and scaling.
- **Mathematical Formulation**:
  - **aHash**: Downsample to $8 \times 8$, threshold against mean intensity.
  - **dHash**: Downsample to $9 \times 8$, compare adjacent horizontal pixels $P[x] > P[x+1]$.
  - **pHash**: Downsample to $32 \times 32$, compute 2D DCT, threshold top-left $8 \times 8$ low frequencies against median.
  - **Hamming Distance**: $D_H(h_1, h_2) = \operatorname{popcount}(h_1 \oplus h_2)$.
- **Parameters**: `reference_phash` (optional 16-hex string).
- **Artifacts**: Hexadecimal fingerprints and similarity score metrics.
- **Insurance Relevance**: High. Detects duplicate claim submissions across different policies or dates where photos were slightly cropped or resized.

---

### 2.7 Edge Gradient & Inpainting Analysis (`resampling`)
- **What It Measures**: Sobel edge gradient magnitude and Laplacian texture variance ($\nabla^2 I$) across spatial blocks.
- **Mathematical Formulation**:
  $$G(x, y) = \sqrt{G_x^2 + G_y^2}, \quad L(x, y) = \nabla^2 I(x, y)$$
  Identifies isolated blocks with an unnatural drop in Laplacian variance surrounded by textured surroundings ($< 15\%$ of median).
- **Parameters**: `block_size` (16 px), `smoothing_ratio_threshold` (0.15).
- **Artifacts**: 2D Sobel gradient magnitude map in Viridis colormap (`EDGE_GRADIENT_MAP`, PNG).
- **Insurance Relevance**: Medium. Flags digital scratch erasure or inpainting where pre-existing vehicle damage was digitally smoothed.

