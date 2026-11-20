# Q-TRACE — Classical Forensic Algorithm Study & Engine Specification

**Document ID:** `DOC-KB-005`  
**Classification:** Computer Vision & Forensics Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Scope:** Classical Signal Processing, Feature Extraction, Metadata, and Evidence Fusion  

---

## 1. Executive Summary

While the Quantum Laboratory provides an advanced scientific environment for patch-level algebraic verification, the **Classical Forensic Engine** is the operational workhorse of Q-TRACE. It analyzes full-resolution, multi-megapixel vehicle damage photographs in seconds, flagging candidate regions of tampering across independent physical, optical, and mathematical domains.

A single forensic algorithm can never be trusted in isolation:
- Error Level Analysis (ELA) flags high-contrast vehicle body lines as false positives.
- SIFT copy-move detection fails on textureless, smooth car hoods.
- Noise analysis fails if an entire image has been uniformly downsampled and re-compressed.

Q-TRACE solves this through **Orthogonal Signal Fusion**: combining five complementary, deterministic algorithms into a unified **Consensus Evidence Map**.

---

## 2. Comprehensive Algorithm Study & Evaluation

```
+---------------------------------------------------------------------------------------------------+
|                              CLASSICAL FORENSIC ALGORITHM ARSENAL                                 |
+---------------------------------------------------------------------------------------------------+
|  1. Error Level Analysis (ELA)               --> Compression history & JPEG quantization anomaly |
|  2. SIFT/ORB Copy-Move Detector (CMFD)       --> Spatial duplication & feature cloning            |
|  3. Median Filter Noise Inconsistency        --> Sensor noise floor variance & foreign splices   |
|  4. Gradient Discontinuity & Inpainting Mask --> Boundary feathering & erased wear               |
|  5. Pixel Reference SSIM Delta               --> Pre-loss vs. post-loss baseline comparison      |
|  6. EXIF & Structural Metadata Parser        --> Timestamp, software signature & thumbnail check  |
+---------------------------------------------------------------------------------------------------+
```

---

### Algorithm 1: Error Level Analysis (ELA)

#### Mathematical Foundation:
Lossy JPEG compression operates by dividing an image into $8 \times 8$ pixel blocks, computing the 2D Discrete Cosine Transform (DCT), and quantizing the frequency coefficients:
$$F_Q(u, v) = \operatorname{round}\left( \frac{\operatorname{DCT}(f(x, y))}{Q(u, v)} \right)$$
where $Q(u, v)$ is the quantization matrix defined by the JPEG quality level.

When an uncompressed image (or an image saved at Quality $Q_1$) is modified by inserting a foreign patch from an image saved at Quality $Q_2$, and the composite image is saved at Quality $Q_{target}$, the resave error rate across the image is non-uniform.

ELA resaves the suspect image $I_{in}$ at a fixed reference quality $Q_{ref} = 95\%$ to produce $I_{resave}$. The absolute pixel error is computed:
$$E(x, y) = |I_{in}(x, y) - I_{resave}(x, y)|$$
To make subtle differences visible, the error is scaled by an enhancement factor $\alpha$ (typically $\alpha = 10 \text{ to } 20$):
$$\operatorname{ELA}(x, y) = \min(255, \alpha \cdot E(x, y))$$

#### Technical Profile:
- **Inputs:** Color image (JPEG, PNG, TIFF).
- **Outputs:** Enhanced error heatmap (grayscale or jet-colormap) highlighting high-error blocks.
- **Strengths:** Blazingly fast ($O(N)$, $< 80 \text{ ms}$ for 12 MP image); extremely effective at revealing digital graphics, cloned panels with different compression histories, and spliced objects.
- **Known Failure Conditions:** High-contrast natural boundaries (e.g., sharp transition between black tire and chrome rim) naturally produce high DCT high-frequency residuals, appearing bright even in authentic photos.
- **Integration:** Implemented via Pillow memory buffer (`io.BytesIO`) without writing temporary files to disk.

---

### Algorithm 2: Keypoint-Based Copy-Move Forgery Detection (SIFT + Spatial Clustering)

#### Mathematical Foundation:
To detect cloned vehicle damage (e.g., duplicating a dent across two panels), Scale-Invariant Feature Transform (SIFT) keypoints are extracted:
1. **Scale-Space Extrema Detection:** Convolve the image with Difference-of-Gaussian (DoG) functions at multiple scales:
   $$D(x, y, \sigma) = (G(x, y, k\sigma) - G(x, y, \sigma)) * I(x, y)$$
2. **Keypoint Descriptor:** For each stable keypoint $\mathbf{x}_i = (x_i, y_i)$, compute a 128-dimensional orientation histogram vector $\mathbf{d}_i \in \mathbb{R}^{128}$.
3. **Feature Matching:** For keypoint $\mathbf{x}_i$, find its nearest neighbors $\mathbf{x}_j$ in descriptor space ($j \neq i$). Match pairs that satisfy Lowe's ratio criterion:
   $$\frac{\|\mathbf{d}_i - \mathbf{d}_{nearest}\|_2}{\|\mathbf{d}_i - \mathbf{d}_{second\_nearest}\|_2} < \tau_{ratio} \quad (\tau_{ratio} \approx 0.65)$$
4. **Spatial Distance Filtering & Clustering:** Genuine physical objects often share textures. To eliminate false matches from adjacent pixels, enforce a minimum spatial distance threshold:
   $$\|\mathbf{x}_i - \mathbf{x}_j\|_2 > d_{min} \quad (d_{min} \ge 30 \text{ pixels})$$
5. **RANSAC / Affine Verification:** Group matching vectors into clusters sharing a common affine transformation $\mathbf{H}$:
   $$\mathbf{x}_j \approx \mathbf{H} \mathbf{x}_i$$

#### Technical Profile:
- **Inputs:** Grayscale or RGB image.
- **Outputs:** Set of matched keypoint pairs, connected vector lines, and convex hull bounding boxes around source and target cloned regions.
- **Strengths:** Robust to rotation (up to $360^\circ$), scale changes ($\pm 50\%$), and additive noise.
- **Known Failure Conditions:** Textureless vehicle panels (smooth white hood) yield zero keypoints.
- **Integration:** OpenCV (`cv2.SIFT_create()`, `cv2.BFMatcher`), fallback to ORB (`cv2.ORB_create()`) for resource-constrained systems.

---

### Algorithm 3: Noise Inconsistency & Sensor Pattern Residuals

#### Mathematical Foundation:
A raw photograph captured by a digital camera sensor can be modeled as:
$$I(x, y) = I_0(x, y) + N(x, y)$$
where $I_0(x, y)$ is the noise-free scene radiance and $N(x, y)$ is zero-mean additive white Gaussian noise representing shot noise, dark current, and PRNU sensor variations with local variance $\sigma^2_N$.

When a foreign patch is spliced into an image, the noise variance $\sigma^2_{patch}$ of the inserted object rarely matches the host camera sensor noise $\sigma^2_{host}$.

1. **Noise Extraction:** Apply a $3 \times 3$ or $5 \times 5$ adaptive median filter or wavelet denoising filter to obtain a denoised estimate $\hat{I}_0(x, y)$:
   $$\hat{N}(x, y) = |I(x, y) - \hat{I}_0(x, y)|$$
2. **Local Noise Variance Estimation:** Partition the residual $\hat{N}$ into overlapping blocks $B_k$ of size $W \times W$ ($W = 16 \text{ to } 32$ pixels). Compute the local variance:
   $$\sigma^2(B_k) = \frac{1}{W^2} \sum_{(x, y) \in B_k} (\hat{N}(x, y) - \mu_{B_k})^2$$
3. **Inconsistency Map:** Compute the global median noise variance $\bar{\sigma}^2$ and flag blocks where $|\sigma^2(B_k) - \bar{\sigma}^2| > \theta_{noise}$.

#### Technical Profile:
- **Inputs:** Grayscale image.
- **Outputs:** Continuous 2D noise variance heatmap.
- **Strengths:** Completely independent of JPEG compression; catches uncompressed or raw image splices that bypass ELA.
- **Known Failure Conditions:** Extreme shadows or blown-out highlights where sensor noise is non-linear.
- **Integration:** NumPy 2D convolution and SciPy signal filtering.

---

### Algorithm 4: Edge Gradient Discontinuity & Inpainting Analysis

#### Mathematical Foundation:
Digital inpainting (used to remove pre-existing scratches or vehicle rust) fills regions using patch synthesis or partial differential equation (PDE) interpolation (e.g., Navier-Stokes, Telea). This process alters high-frequency gradients:
1. **Gradient Delta Calculation:** Compute horizontal and vertical gradients using Sobel operators:
   $$G_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix} * I, \quad G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix} * I$$
   $$G_{mag}(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2}$$
2. **Laplacian Edge Variance:** Inpainted regions exhibit an unnatural drop in Laplacian variance:
   $$L(x, y) = \nabla^2 I(x, y) = \frac{\partial^2 I}{\partial x^2} + \frac{\partial^2 I}{\partial y^2}$$
   Regions with near-zero Laplacian variance surrounded by high-texture bodywork indicate smoothing or erasure.

#### Technical Profile:
- **Inputs:** Grayscale image.
- **Outputs:** Boundary feathering heatmap and smooth-zone candidate masks.
- **Strengths:** Identifies where scratches or dents were digitally erased.
- **Known Failure Conditions:** Unpainted clean plastic or glass sections naturally have low texture variance.

---

### Algorithm 5: Pixel Reference Difference & Structural Similarity (SSIM) Delta

#### Mathematical Foundation:
When an insurer has a verified pre-loss reference photograph (or an undamaged twin photo), direct aligned comparison is performed:
1. **Alignment:** Keypoint homography estimation aligns the test image to the reference image:
   $$\mathbf{x}_{ref} \sim \mathbf{H} \mathbf{x}_{test}$$
2. **Normalized Absolute Difference:**
   $$\Delta I(x, y) = \frac{|I_{ref}(x, y) - I_{test}(x, y)|}{255}$$
3. **Structural Similarity Index (SSIM) Map:**
   $$\operatorname{SSIM}(x, y) = \frac{(2\mu_x \mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$$
   The discrepancy mask is $M_{diff}(x, y) = 1 - \operatorname{SSIM}(x, y)$.

#### Technical Profile:
- **Inputs:** Reference Image + Suspect Image.
- **Outputs:** Exact pixel difference map, SSIM score, and patch coordinates for routing to the Quantum Laboratory.

---

### Algorithm 6: EXIF Structure & Metadata Verification

#### Forensic Checks Performed:
1. **Software Artifact Tagging:** Scans `Software`, `ProcessingSoftware`, `History`, and `XMP` tags for signatures of editing suites (Adobe Photoshop, GIMP, Snapseed, Canva).
2. **Timestamp Coherence:** Compares `DateTimeOriginal`, `DateTimeDigitized`, and filesystem `mtime`/`ctime`. Discrepancies indicate post-capture modification.
3. **Camera Sensor & Lens Model Consistency:** Cross-references camera model with expected focal length, aperture range, and ISO values.
4. **Embedded Thumbnail Discrepancy:** Extracts the JPEG thumbnail stored inside EXIF APP1 header. Many novice fraudsters edit the full-resolution image in Photoshop, which fails to update the embedded thumbnail. Comparing the embedded thumbnail against the downsampled full image exposes the original un-edited scene instantly!
5. **C2PA Manifest Detection:** Checks for the presence of JUMBF containers to verify digital provenance credentials.

---

## 3. Algorithm Comparison & Selection Matrix

| Forensic Algorithm | Primary Target Forgery | Input Requirements | Execution Time (12 MP Image) | RAM Footprint | False Positive Vulnerability | Integration Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Error Level Analysis (ELA)** | Compression splices, added graphics | Single Image | ~75 ms | ~45 MB | High along natural contrast edges | **Core (P0)** |
| **SIFT Copy-Move Detector** | Cloned damage (dents/scratches) | Single Image | ~420 ms | ~85 MB | Low (filtered by distance & clustering) | **Core (P0)** |
| **Median Noise Residual** | Foreign sensor splices, raw pasted patches | Single Image | ~180 ms | ~60 MB | Medium in deep shadows | **Core (P0)** |
| **EXIF & Thumbnail Check** | Metadata tampering, tool traces | Raw File Bytes | ~10 ms | ~5 MB | Very Low | **Core (P0)** |
| **Reference SSIM Delta** | Pre-loss vs. post-loss modifications | Image Pair | ~120 ms | ~70 MB | Low if geometrically aligned | **Core (P0)** |
| **Gradient Delta / Inpaint** | Erased wear, smoothed rust | Single Image | ~95 ms | ~50 MB | Medium on smooth glass/body | **Secondary (P1)** |

---

## 4. Multi-Signal Evidence Fusion Protocol

To prevent investigator cognitive overload, Q-TRACE combines individual algorithmic heatmaps into a calibrated **Consensus Suspicion Mask**.

```
+------------------+     +--------------------+     +------------------+
|   ELA Heatmap    |     | SIFT Cluster Hull  |     |  Noise Heatmap   |
|   H_ELA(x, y)    |     |   H_SIFT(x, y)     |     |   H_Noise(x, y)  |
+------------------+     +--------------------+     +------------------+
         |                         |                          |
         \                         |                          /
          \                        |                         /
           +-----------------------v------------------------+
           |           NORMALIZATION & CALIBRATION          |
           |             [0, 1] Range Rescaling             |
           +------------------------------------------------+
                                   |
                                   v
           +------------------------------------------------+
           |          WEIGHTED CONSENSUS FUSION             |
           |   H_fuse = w1*H_ELA + w2*H_SIFT + w3*H_Noise   |
           +------------------------------------------------+
                                   |
                                   v
           +------------------------------------------------+
           |       MORPHOLOGICAL FILTERING & BLOB CLUSTERING|
           |        Open -> Dilate -> Connected Components  |
           +------------------------------------------------+
                                   |
                                   v
           +------------------------------------------------+
           |           REGION-OF-INTEREST (RoI)             |
           |    Bounding Boxes: [RoI-01, RoI-02, RoI-03]    |
           |       Consensus Score: S_RoI in [0.0, 1.0]     |
           +------------------------------------------------+
                                   |
                                   +--------> [ Route top 4x4 patch to Quantum Lab ]
```

### Fusion Algorithm:
1. **Per-Pixel Fusion:**
   $$H_{fuse}(x, y) = w_{ELA} \tilde{H}_{ELA}(x, y) + w_{SIFT} \tilde{H}_{SIFT}(x, y) + w_{Noise} \tilde{H}_{Noise}(x, y)$$
   where weights $w_i \ge 0, \sum w_i = 1$ (default $w_{ELA} = 0.35, w_{SIFT} = 0.40, w_{Noise} = 0.25$).
2. **Thresholding & Morphology:**
   Binary mask $B(x, y) = \mathbb{I}(H_{fuse}(x, y) > \theta_{consensus})$. Apply morphological opening (kernel $5 \times 5$) to eliminate salt-and-pepper noise, followed by dilation (kernel $7 \times 7$) to bridge neighboring fragments.
3. **Connected Components & RoI Bounding Boxes:**
   Extract contiguous contours. For each component with area $A \ge A_{min}$ ($A_{min} \approx 400 \text{ pixels}$), compute:
   - Bounding box $(x, y, w, h)$.
   - Mean consensus suspicion score $S_{RoI} \in [0.0, 1.0]$.
   - Contributing methods list (e.g., `["ELA", "Noise Inconsistency"]`).
4. **Quantum Lab Handoff:**
   The highest-scoring centroid $(x_c, y_c)$ is extracted as a $4 \times 4$ tile and made available for immediate execution in the 16-qubit Quantum Laboratory.

---

*Continue to `DATASET_RESEARCH.md` for the dataset research and synthetic tampering protocol.*

