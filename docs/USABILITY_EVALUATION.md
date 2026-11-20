# Q-TRACE: Forensic Usability & Investigator Workflow Evaluation

**Document Reference:** `docs/USABILITY_EVALUATION.md`  
**Classification:** Product Experience & Human-Computer Interaction (HCI)  
**Version:** 1.9.0  

---

## 1. Structured Expert Walkthrough Methodology

A forensic investigation workstation must minimize cognitive load, prevent procedural omissions, and enforce chain-of-custody without impeding expert discretion.

We conducted a structured 10-step expert usability walkthrough simulating a real-world motor-vehicle claims investigation:

```
+-------------------------------------------------------------------------------+
|                      10-STEP INVESTIGATION USER JOURNEY                       |
|                                                                               |
|  [1. Intake] ----> [2. Ingestion] ----> [3. WORM Audit] ----> [4. Forensics]  |
|         |                                                            |        |
|  [8. Notes] <---- [7. Quantum] <---- [6. Alignment] <---- [5. Canvas ROI]    |
|         |                                                                     |
|  [9. Dossier] ---> [10. PDF Seal]                                             |
+-------------------------------------------------------------------------------+
```

---

## 2. Walkthrough Evaluation Rubric

| Step | User Workflow Stage | UI Surface / Component | Observed Usability Telemetry | Qualitative Examiner Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Case Creation & Policy Linkage | Command Center / Case Modal | Form validation checks case number uniqueness in $< 50\text{ ms}$. | Clean, straightforward case initialization. |
| **2** | Photographic Evidence Ingestion | Drag-and-drop dropzone | Auto-computes SHA-256 upon drop; displays hex hash immediately. | Instantaneous feedback; reinforces evidence integrity. |
| **3** | Cryptographic Integrity Verification | Evidence Details Drawer | One-click verification compares physical bytes to SQLite ledger. | Clear badge indicator (*VERIFIED_AUTHENTIC* in emerald green). |
| **4** | Classical Forensic Execution | Analysis Execution Drawer | Selective checkbox execution of ELA, Noise, CMFD, and pHash. | Progress spinners and execution times clearly indicated. |
| **5** | Interactive Canvas & ROI Selection | Forensic Canvas (Canvas2D) | Smooth pan/zoom up to 1000%; crosshairs display sub-pixel coordinates. | Responsive 60 FPS viewport manipulation; crisp pixel inspection. |
| **6** | Dual-Image Comparative Inspection | SIFT Homography Comparison | Side-by-side split screen and difference heatmap overlay. | Facilitates direct alignment between pre-accident and claim photos. |
| **7** | Quantum Micro-Patch Experimentation| Quantum Laboratory Page | $4 \times 4$ interactive matrix editor with 16Q/12Q circuit selectors. | Transparent telemetry: displays shots, runtime, and gate depth. |
| **8** | Examiner Notes & Hypotheses | Contextual Annotation Drawer| Categorized entry separating facts, observations, and hypotheses. | Enforces disciplined thinking; prevents premature bias. |
| **9** | Dossier Assembly & Ordering | Dossier Studio | 13-section interactive outline with drag reordering and section toggles.| Intuitive document structuring; live markdown preview. |
| **10**| Cryptographic PDF Export | Report Export Modal | ReportLab generates verified PDF with verification seal in $< 100\text{ ms}$. | Clean, courtroom-ready document formatting. |

