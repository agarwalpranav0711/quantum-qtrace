# Q-TRACE — Product Design, Interaction & UI/UX Specification

**Document ID:** `DOC-KB-007`  
**Classification:** Design System & Human-Computer Interaction (HCI) Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Design Mandate:** Non-Generic, Industrial "Dark Laboratory" Workstation  

---

## 1. Design Philosophy: The Anti-Dashboard Principle

The visual design and user interaction of Q-TRACE are treated as first-class engineering responsibilities. The project owner has explicitly forbidden the standard, generic "AI template dashboard":
- **NO** four colorful metric cards with fake percentages.
- **NO** meaningless purple/pink background gradients.
- **NO** decorative, un-interactive line graphs.
- **NO** bloated, empty card containers with oversized rounded corners.
- **NO** fake AI chatbot popups.

Instead, Q-TRACE is designed to look, feel, and perform like an **Industrial Scientific Workstation**—blending the focused precision of professional evidence suites (Amped Authenticate, Magnet AXIOM) with the clarity of modern scientific visualization tools (ImageJ, IBM Quantum Composer).

Every pixel, border, and visual indicator in Q-TRACE serves an operational purpose: **assisting the investigator in discovering, verifying, and documenting image manipulation.**

---

## 2. Exploration of Three Interface Concepts

To identify the optimal interaction paradigm, we modeled and evaluated three fundamentally distinct interface architectures:

```
+---------------------------------------------------------------------------------------------------+
|                               THREE ARCHITECTURAL UI CONCEPTS                                     |
+---------------------------------------------------------------------------------------------------+
|  CONCEPT 1: Multi-Pane Scientific IDE                                                             |
|  * Layout: Heavy dockable grid, dense menus, persistent left/right/bottom docks.                  |
|  * Analogy: Visual Studio / Eclipse / Blender.                                                    |
|  * Pros: High information density; power-user customization.                                      |
|  * Cons: Overwhelming visual clutter; shrinks the image canvas to a tiny fraction of screen.     |
+---------------------------------------------------------------------------------------------------+
|  CONCEPT 2: The Evidence Canvas & Contextual Inspector (RECOMMENDED)                             |
|  * Layout: Edge-to-edge interactive Evidence Canvas as primary viewport. Minimalist floating HUD  |
|            controls; slide-out Region Inspector; collapsible Quantum Laboratory drawer.          |
|  * Analogy: Figma / modern GIS / professional CAD workstation.                                   |
|  * Pros: Image evidence is the absolute hero; intuitive non-linear exploration; zero distraction. |
|  * Cons: Requires high-performance Canvas2D/WebGL rendering engine.                              |
+---------------------------------------------------------------------------------------------------+
|  CONCEPT 3: Linear Sequential Pipeline (Wizard)                                                   |
|  * Layout: Stepped horizontal wizard: Step 1 (Ingest) -> Step 2 (Scan) -> Step 3 (Report).         |
|  * Analogy: Tax filing software / installer wizard.                                               |
|  * Pros: Extremely simple for non-technical users.                                                |
|  * Cons: Fatal lack of flexibility; real forensic investigations are iterative and non-linear.    |
+---------------------------------------------------------------------------------------------------+
```

### Concept Evaluation Matrix:

| Evaluation Criteria | Concept 1: Scientific IDE | Concept 2: Evidence Canvas (Selected) | Concept 3: Linear Wizard |
| :--- | :--- | :--- | :--- |
| **Image Viewport Dominance** | Poor (35% screen area) | **Exceptional (75–85% screen area)** | Moderate (50% screen area) |
| **Investigative Fluidity** | High | **Very High (Direct manipulation)** | Very Low (Rigid steps) |
| **Visual Polish & Modernity** | Dated / Cluttered | **Sleek, Authoritative, Premium** | Basic / Consumer-grade |
| **Quantum Module Integration** | Separate docked pane | **Dedicated Laboratory Modal/Drawer** | Trailing step |
| **Viva Presentation Impact** | Moderate (Looks like legacy IDE) | **Maximum (Visually stunning & clear)** | Low (Looks like school form) |

**Decision:** **Concept 2 (Evidence Canvas & Precision Inspector)** is selected as the definitive user interface architecture for Q-TRACE.

---

## 3. Visual Design System: "Dark Laboratory"

### 3.1 Design Tokens & Color Palette

The interface utilizes a deep obsidian and graphite palette calibrated for long forensic inspection sessions, eliminating glare while maximizing contrast for multi-channel heatmaps.

```
Color Role                | Token Name        | Hex Value | Semantic Usage
--------------------------+-------------------+-----------+----------------------------------------------
Canvas Void               | --bg-canvas       | #080C14   | Deepest viewport background
Primary Surface           | --bg-surface-1    | #0F172A   | Navigation headers, inspector drawers
Elevated Card             | --bg-surface-2    | #1E293B   | Control panels, modal overlays, tooltips
Subtle Border             | --border-subtle   | #334155   | 1px hairline panel separators
Accent Primary (Active)   | --accent-cyan     | #00E5FF   | Selected tools, active overlays, zoom HUD
Accent Secondary (Quantum)| --accent-quantum  | #818CF8   | Qubit registers, circuit paths, unitary gates
Warning / Anomaly         | --status-anomaly  | #F59E0B   | Flagged suspicious regions, high ELA error
Verified / Intact         | --status-verified | #10B981   | SHA-256 match, valid C2PA, identical pixels
Text Primary              | --text-primary    | #F8FAFC   | High-contrast titles, coordinates, values
Text Secondary            | --text-muted      | #94A3B8   | Metadata labels, timestamps, explanations
```

### 3.2 Typography Hierarchy
- **Primary Interface Font:** `Inter` or `Plus Jakarta Sans` — ultra-clean geometric sans-serif for UI labels, buttons, and navigation.
- **Monospace Technical Font:** `JetBrains Mono` or `Fira Code` — used for SHA-256 hashes, quantum basis state equations ($|0110\rangle$), coordinate readouts `(X: 1042, Y: 850)`, and circuit statistics.

---

## 4. Detailed Specification of Core Workspaces

### 4.1 The Evidence Canvas (Main Viewport)

```
+---------------------------------------------------------------------------------------------------+
|  [ Case: #INS-2026-9042 ]  [ SHA-256: e3b0c44298fc1c149afbf4c899... ]       [ Zoom: 240% ] [Fit] |
+---------------------------------------------------------------------------------------------------+
|                                                                                |                  |
|                                                                                |  LAYER VISIBILITY|
|                                                                                |  [x] Base Photo  |
|                                                                                |  [x] ELA Heatmap |
|                      +-----------------------------+                           |  [ ] SIFT Vectors|
|                      |  SUSPICIOUS ROI-01          |                           |  [x] Noise Floor |
|                      |  Score: 0.88 (High)         |                           |  [x] RoI BBoxes  |
|                      |  Contributions:             |                           |  ----------------|
|                      |  - ELA Quantization Mismatch|                           |  OPACITY SLIDER  |
|                      |  - Foreign Noise Variance   |                           |  [===>      ] 45%|
|                      +-----------------------------+                           |  ----------------|
|                                                                                |  SPLIT COMPARISON|
|                                                                                |  [ Original | Mod]
|                                                                                |                  |
|                                                                                |  [ Launch Q-Lab ]|
|                                                                                |                  |
+--------------------------------------------------------------------------------+------------------+
|  STATUS: (X: 412, Y: 320) | RGB: (142, 138, 140) | Method: Consensus Alert | Timeline: 6 Events |
+---------------------------------------------------------------------------------------------------+
```

#### Canvas Interaction Model:
1. **Pan & Smooth Zoom:** Mouse wheel zoom centered on cursor from 10% to 3200% magnification; click-and-drag spacebar pan. Pixel interpolation switches from bilinear to nearest-neighbor above 400% for pixel-grid inspection.
2. **Interactive Split-Screen Swipe:** A draggable vertical divider allowing the examiner to wipe between the original reference photograph and the suspect image in real time.
3. **Multi-Channel Overlay Blending:** Independent toggle switches and alpha sliders for each forensic modality (ELA, SIFT vectors, Noise Residuals, Consensus Mask).
4. **Coordinate Inspector Tooltip:** Real-time HUD showing exact pixel coordinates, raw RGB values, local variance, and contributing algorithmic scores at the cursor position.

---

### 4.2 The Region Inspector (Contextual Side Drawer)

When the investigator clicks any bounding box or draws a custom marquee selection:
- **Region Crop View:** Instant 1:1 pixel-accurate crop of the selected region.
- **Multi-Method Evidence Breakdown:** Horizontal indicator bars showing confidence metrics from each active algorithm:
  - *Error Level Analysis:* $\Delta Q = +34.2\%$ (Flagged)
  - *SIFT Keypoint Matching:* 0 duplicate keypoint vectors (Clear)
  - *Noise Inconsistency:* $\sigma^2_{patch} = 14.2 \text{ vs. } \bar{\sigma}^2_{host} = 3.8$ (Severe Anomaly)
- **Forensic Interpretation Notes:** Bulleted explanation:  
  *"The selected dent region contains high-frequency compression residuals inconsistent with adjacent quarter-panel bodywork. Noise variance suggests the damage was spliced from a secondary camera sensor."*
- **Examiner Commentary Field:** Free-text input where the investigator records human observations to be directly bound into the case report.
- **One-Click Quantum Handoff:** Button `[ Send 4x4 Patch to Quantum Lab ]` that downsamples/crops the high-suspicion core into the quantum engine.

---

### 4.3 The Quantum Laboratory Interface

The Quantum Laboratory opens as an immersive technical modal or sliding drawer:

```
+---------------------------------------------------------------------------------------------------+
|  QUANTUM LABORATORY — NEQR IMAGE COMPARISON EXPERIMENT                                       [ X ]|
+---------------------------------------------------------------------------------------------------+
|  PATCH CONFIGURATION                 CIRCUIT VISUALIZER (Qiskit Render)                           |
|  Patch: Centroid (412, 320)          |q0: Pos_Y0> --[ H ]----*------------------------- [ M ]    |
|  Dimension: 4x4 (16 pixels)          |q1: Pos_Y1> --[ H ]----|----*-------------------- [ M ]    |
|  Precision: 4-bit Grayscale          |q2: Pos_X0> --[ H ]----|----|----*--------------- [ M ]    |
|                                      |q3: Pos_X1> --[ H ]----|----|----|----*---------- [ M ]    |
|  CIRCUIT METRICS                     |q4: Orig_0> -----------X----|----|----|---*------ [   ]    |
|  Qubits: 16 (4 pos, 4 A, 4 B, 4 D)   |q8: Mod_0 > ----------------X----|----|---|---|-- [   ]    |
|  Circuit Depth: 42                   |q12:Diff_0> ---------------------X----X---|---|-- [ M ]    |
|  Gate Count: 136 (8 CNOT XOR)        -------------------------------------------------------------|
|                                      MEASUREMENT HISTOGRAM & RECONSTRUCTION                       |
|  SIMULATION CONTROLS                 Shot Count: 1024 | Simulator: Aer QasmSimulator              |
|  Shots: [ 1024      ] (Slider)       Observed Distinct States: 16 / 16 (100% Coverage)            |
|  [ Execute Quantum Simulation ]      Discrepancy Status: 3 Altered Pixels Detected                |
|                                      Difference Map Reconstruction: [ 4x4 Heatmap Rendered ]      |
+---------------------------------------------------------------------------------------------------+
```

#### Key Quantum Lab Features:
1. **Interactive Circuit Diagram:** Scrollable, high-definition SVG render of the exact Qiskit circuit generated for the active patch, showing position Hadamard gates, controlled state-preparation gates, and comparison CNOTs.
2. **Qubit Register Inspector:** Clear color-coded labeling distinguishing the four functional registers (Position, Image A, Image B, Difference).
3. **Shot Budget Slider:** Allows the student/examiner to vary measurement shots between 16 and 4096. Demonstrates in real time how low shot counts ($S < 54$) fail to reconstruct the full difference map due to the Coupon Collector's limit, whereas $S \ge 1024$ produces perfect fidelity.
4. **Probability Amplitude Distribution:** Plotly/Chart.js histogram displaying empirical basis state counts versus theoretical uniform probabilities ($1/16 = 6.25\%$).
5. **Reconstructed Spatial Difference Map:** The 16 sampled basis states are decoded back into a $4 \times 4$ pixel difference matrix and displayed side-by-side with classical pixel subtraction.

---

### 4.4 The Forensic Timeline

A chronological, immutable audit log displayed along the bottom/side:
- `10:14:02` — **Evidence Ingested:** `claim_photo_01.jpg` (SHA-256: `e3b0c44...`)
- `10:14:03` — **Integrity Manifest Sealed:** Saved to WORM storage
- `10:14:05` — **Classical Scan Complete:** ELA, SIFT, Noise analyses executed
- `10:15:20` — **RoI-01 Created:** Examiner selected suspicious door crease
- `10:16:10` — **Quantum Experiment #1 Executed:** 1024 shots, 3 discrepancy pixels verified
- `10:18:45` — **Case Report Generated:** Exported to signed PDF `Report-INS-9042.pdf`

Every timeline node is clickable, instantly restoring the canvas view to that historical state.

---

*Continue to `SYSTEM_ARCHITECTURE.md` for the technical architecture, component schema, and technology selections.*

