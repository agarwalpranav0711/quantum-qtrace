# Q-TRACE — Risk Register, Feasibility Limits & Mitigation Matrix

**Document ID:** `DOC-KB-010`  
**Classification:** Risk Assessment & Engineering Contingency Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Review Target:** Academic Review Board & Software Quality Gate  

---

## 1. Risk Governance & Severity Methodology

To guarantee that Q-TRACE can be delivered on schedule, with zero runtime failures, and survive rigorous academic examination, all technical risks are classified using a standard $3 \times 3$ Risk Matrix:
- **Severity:** High (Catastrophic/Blocker), Medium (Degraded Experience), Low (Cosmetic/Minor).
- **Likelihood:** High ($> 50\%$), Medium ($20–50\%$), Low ($< 20\%$).
- **Risk Score:** $\text{Severity} \times \text{Likelihood}$.

Every risk is paired with a **Primary Engineering Mitigation** and an **Explicit Fallback Protocol**.

---

## 2. Comprehensive Risk Assessment Matrix

```
+---------------------------------------------------------------------------------------------------+
|                                      RISK REGISTER TAXONOMY                                       |
+---------------------------------------------------------------------------------------------------+
|  CATEGORY 1: Quantum Computing & Simulation Risks (QR-01 to QR-05)                                |
|  CATEGORY 2: Classical Forensic & Computer Vision Risks (CR-01 to CR-05)                          |
|  CATEGORY 3: Product, Engineering & Platform Risks (PR-01 to PR-05)                               |
+---------------------------------------------------------------------------------------------------+
```

---

### Category 1: Quantum Computing & Simulation Risks

| Risk ID | Risk Description | Severity | Likelihood | Impact on Project | Primary Mitigation Strategy | Emergency Fallback Protocol |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QR-01** | **Exponential State Preparation Complexity:** Compiling $C^4(NOT)$ gates for 16 pixels generates hundreds of elementary gates, slowing down compilation. | **High** | **High** | High latency in Quantum Lab execution (> 3 seconds). | Use Qiskit's optimized unitary decomposition (`transpile` with `optimization_level=1`); cache parameterized gate templates for $4 \times 4$ coordinates. | Fall back to pre-compiled state preparation subcircuits, reducing transpilation overhead to $< 100 \text{ ms}$. |
| **QR-02** | **Simulator RAM Exhaustion (> 28 Qubits):** Attempting to simulate larger images ($16 \times 16$ or $512 \times 512$) instantly exhausts laptop RAM. | **High** | **Low** | Application crash (`MemoryError` / OOM kill). | Hard-lock the Quantum Laboratory strictly to $4 \times 4$ (16 qubits) or $8 \times 8$ (18 qubits) patch tiles. Reject any patch exceeding 18 qubits at the API gateway. | Display an educational alert modal: *"Classical simulation limits quantum state vectors to $\le 18$ qubits. Patch tiling applied."* |
| **QR-03** | **Shot Noise & Missing Pixels (Coupon Collector):** Investigator executes circuit with low shot budget ($S < 50$), leaving 30% of pixels unmeasured. | **Medium** | **High** | Incomplete difference map; confusing visual output. | Set default shot budget to $S = 1024$ in UI; highlight unobserved pixels in amber with an informative tooltip: *"State unobserved: Increase shot budget."* | Provide an automatic "Shot Recommendation" badge showing theoretical coverage probability for the selected slider value. |
| **QR-04** | **Viva Reviewer Skepticism on "Quantum Advantage":** Examiner asks: *"Why use Qiskit when OpenCV does this in 50 nanoseconds?"* | **High** | **High** | Potential failure or point deduction during academic viva. | **Proactive Academic Candor:** Explicitly present Experiment 10 (Resource Benchmark) in the report and viva deck. State clearly that Q-TRACE demonstrates **algorithmic formulation for future fault-tolerant hardware** and Grover-search quadratic speedups, not present-day NISQ simulation superiority. | Emphasize the educational, exploratory mandate of the Quantum Laboratory as a core university capstone learning objective. |
| **QR-05** | **Qiskit Aer Windows Wheel Incompatibility:** Breaking changes in new Qiskit 1.0+ releases on Windows. | **Medium** | **Low** | Backend fails to start or import `qiskit_aer`. | Pin verified versions in `requirements.txt` (`qiskit>=1.0.0`, `qiskit-aer>=0.13.0`); provide verified PowerShell installation script. | Implement a fallback pure-Python state vector matrix simulator for the 16-qubit circuit if native Aer fails. |

---

### Category 2: Classical Forensic & Computer Vision Risks

| Risk ID | Risk Description | Severity | Likelihood | Impact on Project | Primary Mitigation Strategy | Emergency Fallback Protocol |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CR-01** | **False Positives on Natural High-Contrast Edges:** ELA flags sharp car outlines (black tire vs. white rim) as manipulated. | **High** | **High** | Loss of investigator trust; false alarm clutter. | **Multi-Signal Consensus Fusion:** Never display ELA in isolation. Require corroboration from Noise Inconsistency or SIFT before promoting an anomaly to a primary RoI. | Provide an "Edge Masking Filter" toggle that suppresses high-contrast Sobel edges from the ELA heatmap. |
| **CR-02** | **SIFT Failure on Smooth Vehicle Bodywork:** Flat, textureless car door or hood panels generate zero keypoints, causing copy-move detection to fail. | **Medium** | **High** | Undetected smooth paint cloning. | Supplement SIFT with dense block-based DCT matching or ORB corner detectors; inspect noise variance across smooth panels. | Clearly document limitation in the UI Inspector: *"Textureless region: SIFT descriptor density too low. Rely on Noise & ELA signals."* |
| **CR-03** | **JPEG Re-compression Scrubbing Traces:** An image shared via messaging apps (WhatsApp, Telegram) is re-compressed at $Q=70$, washing out subtle compression and noise fingerprints. | **High** | **Medium** | Subdued ELA and noise heatmaps. | Detect multi-compression signatures using JPEG DCT coefficient histogram analysis; display a **Compression Degradation Warning** badge in the UI. | Fall back to structural geometric analysis, reference SSIM comparison, and EXIF thumbnail discrepancy checks. |
| **CR-04** | **Non-Rigid Vehicle Deformation Misalignment:** Pre-loss vs. post-loss vehicle photos have slightly different angles or lighting, creating global difference clutter. | **Medium** | **High** | Spurious pixel difference noise across entire vehicle. | Use ORB/SIFT feature-based homography alignment (`cv2.findHomography` with RANSAC) to warp and align images prior to SSIM comparison. | Limit direct comparison to localized, flat planar patches rather than full vehicle bodies. |
| **CR-05** | **Dataset Licensing Conflicts:** Academic datasets (CASIA, CoMoFoD) have strict non-commercial educational licenses. | **Low** | **Low** | Legal ambiguity. | Maintain complete compliance: Q-TRACE is an educational B.Tech project; do not bundle raw dataset binaries into Git; download via verified academic request scripts. | Use 100% synthetically generated open test images for standard public repository demos. |

---

### Category 3: Product, Engineering & Platform Risks

| Risk ID | Risk Description | Severity | Likelihood | Impact on Project | Primary Mitigation Strategy | Emergency Fallback Protocol |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PR-01** | **Scope Creep Threatening Timely Delivery:** Attempting to build an entire operating system, deep learning pipelines, and cloud sync simultaneously. | **High** | **Medium** | Unfinished, buggy submission. | **Strict Phased Delivery:** Strict adherence to Parts 2 through 10. Defer heavy deep learning models (PyTorch) to optional post-capstone extensions. Prioritize core deterministic classical + quantum engines. | Strip non-essential features (e.g., multi-user authentication) to safeguard the core Evidence Canvas and Quantum Lab. |
| **PR-02** | **Decompression Bomb Memory Spike:** Investigator uploads an ultra-high-resolution image (e.g., $10,000 \times 10,000$ pixels) that crashes the Python backend. | **High** | **Low** | Denial of Service / server crash. | Enforce `Image.MAX_IMAGE_PIXELS = 100_000_000` in Pillow; downsample working derivatives to max dimension 2048px for interactive canvas rendering. | Stream original image in raw chunks directly to vault without loading full uncompressed raster into memory. |
| **PR-03** | **Windows Path Traversal & Slash Inconsistency:** Windows backslashes (`\`) vs. POSIX forward slashes (`/`) causing path corruption in FastAPI endpoints. | **Medium** | **High** | Broken image links on Windows 11. | Use Python's `pathlib.Path` consistently across all backend modules; sanitize all filenames with `os.path.basename`. | Never expose raw local filesystem paths to the frontend API; use opaque UUIDs and dedicated static streaming routes. |
| **PR-04** | **Canvas2D Lag on High-Resolution Zooms:** Client-side React rendering stutters when panning 12-megapixel images. | **Medium** | **Medium** | Sluggish, amateur-feeling user experience. | Render image derivatives at optimal display resolutions; implement off-screen canvas buffers; throttle mousemove wheel handlers using `requestAnimationFrame`. | Provide a 1-click "Draft Mode" toggle that scales viewport resolution during fast panning. |
| **PR-05** | **Broken PDF Report Generation (ReportLab Windows Fonts):** Missing system fonts or layout overflows causing PDF export crashes during live demo. | **High** | **Low** | Inability to generate final forensic report. | Use built-in standard PDF core fonts (`Helvetica`, `Courier`, `Times-Roman`); wrap report generation in automated end-to-end regression tests. | Maintain a pre-formatted HTML-to-print CSS fallback report viewable directly in the web browser. |

---

## 3. What to Simplify or Defer if Deadlines Tighten

To ensure absolute delivery of an exceptionally polished product, we define a clear **Feature Triage Hierarchy**:

```
+---------------------------------------------------------------------------------------------------+
|                                     FEATURE TRIAGE HIERARCHY                                      |
+---------------------------------------------------------------------------------------------------+
|  TIER 1: CORE UNCOMPROMISING MUST-HAVES (Parts 2 - 7)                                             |
|  * 16-qubit Qiskit NEQR simulation with circuit visualization and difference map reconstruction.   |
|  * Classical Forensic Engine: ELA, SIFT copy-move, Noise variance, and EXIF parser.               |
|  * WORM evidence vault with SHA-256 manifest integrity.                                           |
|  * React/Canvas2D Evidence Canvas with pan, zoom, layer toggles, and RoI inspector.                |
|  * Deterministic PDF forensic dossier generator.                                                  |
+---------------------------------------------------------------------------------------------------+
|  TIER 2: SECONDARY REFINEMENTS (Parts 8 - 9)                                                      |
|  * Multi-method weighted consensus heatmap fusion.                                                |
|  * Draggable split-screen swipe comparison tool.                                                  |
|  * Detailed forensic timeline audit log.                                                          |
|  * Grover search discrepancy flag demonstration.                                                  |
+---------------------------------------------------------------------------------------------------+
|  TIER 3: OPTIONAL FUTURE EXTENSIONS (Defer if Necessary)                                         |
|  * Deep Learning PyTorch models (ManTra-Net, TruFor).                                             |
|  * Full C2PA JUMBF cryptographic signature re-signing.                                            |
|  * Video file forensics or multi-frame temporal alignment.                                        |
+---------------------------------------------------------------------------------------------------+
```

---

*Continue to `IMPLEMENTATION_ROADMAP.md` for the step-by-step master roadmap for Parts 2 through 10.*

