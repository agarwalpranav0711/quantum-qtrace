# Q-TRACE Copy-Move Forgery Detection (CMFD) Methodology

**Document ID:** `DOC-MET-003`  
**Classification:** Keypoint Analysis & Geometric Clustering  
**Version:** 1.0.0 (Part 5 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Forensics Engineering Team

---

## 1. Principles of Copy-Move Forgery Detection

Copy-Move Forgery occurs when an examiner, claimant, or repair shop duplicates a region of an image and pastes it elsewhere within the same photograph—most commonly duplicating existing panel dents or scratches across multiple doors, fenders, or bumpers to artificially inflate repair estimates.

Because the copied region originates from the same photograph, it shares identical:
- Color distributions and lighting.
- JPEG compression quantization history.
- Camera sensor noise profile.

As a consequence, **pixel-difference and compression algorithms (such as ELA) frequently fail to detect copy-move cloning**. Scale-Invariant Feature Transform (SIFT) keypoint matching is required to detect spatial feature replication.

---

## 2. Keypoint Extraction & Matching Algorithm

```mermaid
flowchart TD
    IMG[Original Evidence Grayscale] --> DETECT[SIFT Feature Detector<br/>Scale-Space Extrema]
    DETECT --> DESC[128-Dim Gradient Descriptors<br/>d_i in R^128]
    DESC --> KNN[4-NN Descriptor Matcher<br/>Self-Match Exclusion]
    KNN --> RATIO{Lowe's Ratio Test<br/>d_cand / d_denom &lt; 0.68}
    RATIO -->|Pass| DIST{Spatial Distance Filter<br/>||x_i - x_j|| &gt;= 35 px}
    DIST -->|Pass| CLUSTER[Parallel Displacement Clustering<br/>Delta x, Delta y, Angle Consistency]
    CLUSTER --> ROI[Extract Source &amp; Cloned Bounding Boxes<br/>+ Dual 4x4 Quantum Patches]
```

### 2.1 Scale-Space Feature Detection
SIFT identifies stable local extrema across Difference-of-Gaussian (DoG) scale spaces:
$$D(x, y, \sigma) = (G(x, y, k\sigma) - G(x, y, \sigma)) * I(x, y)$$
For each stable keypoint $\mathbf{x}_i = (x_i, y_i)$, a 128-dimensional orientation histogram descriptor $\mathbf{d}_i$ is constructed.

### 2.2 4-NN Descriptor Matching & Self-Match Elimination
When matching an image against itself, standard 1-NN matching trivially matches keypoint $i$ to keypoint $i$ (distance = 0.0). Q-TRACE requests $k = 4$ nearest neighbors:
- `m[0]` is the self-match ($d = 0.0$).
- `m[1]` is the candidate twin keypoint.
- `m[2]` is the second nearest non-identical keypoint used as denominator for Lowe's ratio test:
  $$\frac{\|\mathbf{d}_i - \mathbf{d}_{m[1]}\|_2}{\|\mathbf{d}_i - \mathbf{d}_{m[2]}\|_2} < \tau_{ratio} \quad (\tau_{ratio} \approx 0.68)$$

### 2.3 Spatial Distance Filtering
Naturally adjacent pixels often exhibit identical textures. To eliminate false matches between contiguous pixels, Q-TRACE enforces a minimum Euclidean spatial distance threshold:
$$\|\mathbf{x}_i - \mathbf{x}_{twin}\|_2 \ge d_{min} \quad (d_{min} = 35 \text{ pixels})$$

---

## 3. Spatial Displacement Vector Clustering

A genuine copy-move manipulation replicates a coherent physical patch. Therefore, all matched keypoints belonging to the cloned patch must share approximately parallel displacement vectors:
$$\vec{v}_{ij} = \mathbf{x}_j - \mathbf{x}_i = (\Delta x, \Delta y)$$
$$\text{Distance} = \|\vec{v}_{ij}\|_2, \quad \theta_{ij} = \operatorname{atan2}(\Delta y, \Delta x) \pmod{180^\circ}$$

Pairs are clustered if their displacement distance differs by $< 20\%$ and their displacement angles differ by $< 15^\circ$. If a cluster contains $\ge 3$ consistent keypoint vectors, it is designated as a candidate copy-move forgery.

---

## 4. Dual RoI & Dual 4×4 Quantum Lab Extraction

For each verified cluster:
1. Compute the bounding box $(s_x, s_y, s_w, s_h)$ enclosing all source keypoints.
2. Compute the bounding box $(t_x, t_y, t_w, t_h)$ enclosing all destination keypoints.
3. Extract quantized $4 \times 4$ patches from both the source centroid and destination centroid.
4. This enables a unique **cross-laboratory verification**: the examiner can load Patch A (source dent) and Patch B (candidate cloned dent) directly into the Quantum Laboratory to execute quantum XOR subtraction between the candidate duplicate pair!

