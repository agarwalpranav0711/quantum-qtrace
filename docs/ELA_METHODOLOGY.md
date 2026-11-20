# Q-TRACE Error Level Analysis (ELA) Methodology

**Document ID:** `DOC-MET-001`  
**Classification:** Deep-Dive Algorithmic Methodology  
**Version:** 1.0.0 (Part 5 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Forensics Engineering Team

---

## 1. Mathematical & Physical Principles of ELA

### 1.1 JPEG Quantization & Rate-Distortion Theory
Lossy JPEG compression partitions an image into $8 \times 8$ pixel blocks, transforms spatial luminance/chrominance values into the frequency domain via the 2D Discrete Cosine Transform (DCT):

$$F(u, v) = \frac{1}{4} C(u) C(v) \sum_{x=0}^{7} \sum_{y=0}^{7} f(x, y) \cos\left[ \frac{(2x+1)u\pi}{16} \right] \cos\left[ \frac{(2y+1)v\pi}{16} \right]$$

Frequency coefficients are then quantized using a quality-dependent quantization matrix $Q(u, v)$:

$$F_Q(u, v) = \operatorname{round}\left( \frac{F(u, v)}{Q(u, v)} \right)$$

This quantization discards subtle high-frequency details. When an image is re-saved at the same or higher quality level, the rate of change per re-save decreases asymptotically towards an equilibrium state.

### 1.2 Differential Error Under Splicing
If an image consists of elements from two different sources:
- Host vehicle photo saved at Quality $Q_{host} = 75\%$
- Foreign inserted dent/scratch graphic saved at Quality $Q_{patch} = 95\%$
- Composite image saved at Quality $Q_{final} = 85\%$

The amount of error introduced upon re-compressing the entire composite image at a fixed reference quality $Q_{ref} = 95\%$ is non-uniform across the spatial domain:
- Regions previously saved at lower quality ($Q = 75\%$) undergo substantial modification to match the $95\%$ quantization grid.
- Regions previously saved at or near $95\%$ undergo minimal modification.

The absolute error image is computed:
$$E(x, y) = |I_{orig}(x, y) - I_{resaved}(x, y)|$$

To make these microscopic variations discernible to a human examiner, Q-TRACE applies linear amplification with ceiling clamping:
$$\operatorname{ELA}(x, y) = \min(255, \alpha \cdot E(x, y)) \quad (\alpha \in [5, 30])$$

---

## 2. Mitigation of Natural High-Contrast Edge False Positives

A well-known vulnerability of basic ELA is that natural high-contrast boundaries (e.g., sharp vehicle body seams, chrome molding, tire rims, license plate letters) naturally possess significant high-frequency DCT power, producing bright ELA bands even in pristine, authentic photos.

### Q-TRACE Sobel Edge Masking Algorithm:
1. Compute horizontal and vertical gradients using $3 \times 3$ Sobel operators:
   $$G_x = \operatorname{Sobel}_x(I_{gray}), \quad G_y = \operatorname{Sobel}_y(I_{gray})$$
   $$G_{mag}(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2}$$
2. Compute the 85th percentile edge magnitude threshold $\theta_{edge} = P_{85}(G_{mag})$.
3. Construct a non-edge binary mask:
   $$M_{non\_edge}(x, y) = \mathbb{I}(G_{mag}(x, y) < \theta_{edge})$$
4. When calculating block-level re-compression error over $16 \times 16$ blocks, evaluate only pixels within $M_{non\_edge}$. If a block contains $> 70\%$ natural high-contrast edge pixels, its error contribution is zeroed out, preventing false alarms along natural car panel contours.

---

## 3. Quantitative Anomaly Detection & Quantum Patch Extraction

### 3.1 Statistical Anomaly Thresholding
The image is segmented into non-overlapping $16 \times 16$ pixel blocks $B_{r, c}$. For each block satisfying the edge-mask criterion:
$$\mu(B_{r, c}) = \frac{1}{|B_{r, c} \cap M_{non\_edge}|} \sum_{(x, y) \in B_{r, c} \cap M_{non\_edge}} E(x, y)$$

Across all valid blocks, compute the global mean $\bar{\mu}_B$ and standard deviation $\sigma_B$. A block is flagged as anomalous if:
$$\mu(B_{r, c}) > \bar{\mu}_B + \tau_{std} \cdot \sigma_B \quad (\tau_{std} = 2.5)$$

### 3.2 Connected Component Clustering & Bounding Boxes
Connected 8-neighborhood components of anomalous blocks are grouped using `cv2.connectedComponentsWithStats()`. Components with area $\ge 2$ blocks ($32 \times 32$ px) form candidate Regions of Interest (RoIs).

### 3.3 Centroid 4×4 Quantum Patch Extraction
For each candidate RoI with centroid $(c_x, c_y)$, Q-TRACE extracts a $4 \times 4$ pixel sub-grid centered at $(c_x, c_y)$ and quantizes 8-bit values $[0, 255]$ down to 4-bit $[0, 15]$ via bit-shifting (`arr >> 4`):
$$P_{quantum}[r, c] = \operatorname{floor}\left( \frac{I_{gray}[c_y - 2 + r, c_x - 2 + c]}{16} \right)$$
This matrix is pre-formatted for direct handoff to the 16-qubit Quantum Laboratory for algebraic verification.

---

## 4. Examiner Interpretation Guide for Vehicle Insurance Fraud

| Visual ELA Pattern | Physical Forensic Interpretation | Recommended Action |
| :--- | :--- | :--- |
| **Uniform, low-level speckle across entire car body** | Natural single-generation JPEG compression. No compression history conflict detected. | Check other orthogonal signals (Noise, SIFT). |
| **Bright isolated patch on smooth car door panel** | Foreign graphic, spliced dent, or pasted scratch with conflicting quantization tables. | Inspect bounding box coordinates; export 4×4 patch to Quantum Lab. |
| **Bright continuous lines following car hood seams** | High-frequency DCT edge artifact (normal physics). Edge-masking suppresses these automatically. | Disregard as false positive unless accompanied by noise inconsistency. |
| **Completely black / zero-error image** | Image was re-saved at 100% quality (lossless DCT quantization) or is an uncompressed raster. | Re-run ELA at Quality 85 or inspect EXIF software tags. |

