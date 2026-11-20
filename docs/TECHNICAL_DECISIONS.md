# Q-TRACE — Technical Decision Records (ADR / TDR)

**Document ID:** `DOC-KB-012`  
**Classification:** Architectural Decision Records (ADR)  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Format:** Michael Nygard Architectural Decision Record Template  

---

## 1. Index of Architectural Decisions

- **ADR-001:** Dedicated 16-Qubit NEQR Register Architecture vs. 12-Qubit In-Place Representation
- **ADR-002:** Forensic Patch Tiling Paradigm for Quantum Image Processing
- **ADR-003:** Decoupled FastAPI + React Architecture vs. Monolithic Streamlit
- **ADR-004:** Cryptographic WORM Storage & SHA-256 Chain of Custody Ingestion
- **ADR-005:** Orthogonal Multi-Signal Forensic Fusion vs. Monolithic Deep Learning Model
- **ADR-006:** SQLite with Write-Ahead Logging (WAL) for Local Data Persistence
- **ADR-007:** Passive C2PA Provenance Extraction without Hard Signing Dependencies
- **ADR-008:** Pure-Python ReportLab Engine for Deterministic PDF Generation
- **ADR-009:** Standard 1024-Shot Measurement Budget for Complete Spatial Reconstruction
- **ADR-010:** Zero-Cloud, Zero-GPU Local Windows 11 Runtime Execution Guarantee

---

## 2. Architectural Decision Records

---

### ADR-001: Dedicated 16-Qubit NEQR Register Architecture vs. 12-Qubit In-Place Representation

- **Status:** **Approved**
- **Context:** To compare two $4 \times 4$ grayscale images in NEQR representation, we can either allocate a separate 4-qubit difference register $|D\rangle$ (16 qubits total: 4 pos, 4 A, 4 B, 4 D) or perform the XOR in-place targeting Register B ($|B\rangle \to |A \oplus B\rangle$, 12 qubits total).
- **Decision:** Implement the **16-qubit dedicated difference register as the primary architecture**, while retaining the 12-qubit in-place model as a high-speed execution mode.
- **Alternatives Considered:** 
  1. *12-Qubit In-Place XOR:* Overwrites Image B; saves 4 qubits ($93.75\%$ RAM reduction), but requires uncomputing if Image B needs to be re-read.
  2. *FRQI Single-Qubit Rotation:* Rejected because amplitude tomography prevents exact algebraic bitwise XOR.
- **Consequences & Trade-offs:** 
  - *Positive:* The 16-qubit circuit provides complete pedagogical and visual clarity for the university viva. The circuit diagram visibly depicts separate input registers $|A\rangle$ and $|B\rangle$ feeding into output register $|D\rangle$.
  - *Negative:* Simulating 16 qubits requires $1.05 \text{ MB}$ of state vector RAM compared to $65.5 \text{ KB}$ for 12 qubits, though both are trivial on standard laptops.
- **Evidence:** Tested and validated in `QUANTUM_FEASIBILITY.md`.

---

### ADR-002: Forensic Patch Tiling Paradigm for Quantum Image Processing

- **Status:** **Approved**
- **Context:** Full photographic evidence images in motor insurance claims have multi-megapixel resolutions ($3000 \times 2000$ to $4000 \times 3000$). Simulating a full-scale NEQR image classically requires $\approx 42$ qubits (> 70 Terabytes of RAM), which is impossible on a personal computer.
- **Decision:** Adopt the **Forensic Patch Tiling Paradigm**: The Classical Forensic Engine scans the full-resolution image to identify high-suspicion clusters. The highest-scoring candidate centroid is extracted as a $4 \times 4$ (or $8 \times 8$) tile and routed to the 16-qubit Quantum Laboratory for deep algebraic verification.
- **Alternatives Considered:**
  1. *Downsampling entire image to $4 \times 4$:* Completely destroys fine vehicle damage details (a scratch or crack vanishes).
  2. *Claiming full-image quantum simulation:* Scientifically fraudulent and impossible.
- **Consequences & Trade-offs:**
  - *Positive:* Scientifically defensible; enables real, working quantum simulation on a standard laptop in under 200 ms.
  - *Negative:* The quantum module verifies localized patches rather than the entire photograph at once.

---

### ADR-003: Decoupled FastAPI + React Architecture vs. Monolithic Streamlit

- **Status:** **Approved**
- **Context:** We evaluated whether to build Q-TRACE using a rapid Python UI framework (Streamlit) or a decoupled client-server architecture (FastAPI + React 18 + Vite + TypeScript).
- **Decision:** Build a **Decoupled Architecture using FastAPI and React with HTML5 Canvas2D**.
- **Alternatives Considered:**
  1. *Streamlit:* Extremely fast to scaffold, but its execution model reruns the entire Python script on every user interaction. This creates unacceptable lag during image zooming, prevents smooth 60 FPS split-screen wipes, and makes custom layer blending impossible.
  2. *PyQt / PySide Desktop:* Cross-platform GUI, but dated visual aesthetics, poor animation support, and difficult web/presentation portability.
- **Consequences & Trade-offs:**
  - *Positive:* Exceptional UI performance; 60 FPS interactive Canvas2D navigation; modern dark-laboratory visual design; clean OpenAPI separation.
  - *Negative:* Requires managing two development runtimes (Node.js for frontend, Python for backend), mitigated via automated PowerShell orchestration scripts.

---

### ADR-004: Cryptographic WORM Storage & SHA-256 Chain of Custody Ingestion

- **Status:** **Approved**
- **Context:** In legal and insurance investigations, evidence must be tamper-proof. Operating in-place on uploaded photographs destroys original evidence and renders findings inadmissible.
- **Decision:** Implement **Write-Once-Read-Many (WORM) storage**: Upon upload, the raw byte stream is hashed using NIST FIPS 180-4 SHA-256 and written to `storage/vault/{sha256}.bin` with read-only filesystem permissions. All forensic operations execute strictly on in-memory buffers or generated working derivatives.
- **Alternatives Considered:**
  1. *In-place file processing:* High risk of accidental file modification.
  2. *Blockchain / Distributed Ledger:* Unnecessary complexity, slow transaction times, and zero added security for local single-examiner workstations.
- **Consequences & Trade-offs:**
  - *Positive:* Complies with ISO/IEC 27037 digital evidence preservation standards; establishes an unimpeachable audit trail.
  - *Negative:* Slight disk storage duplication (original vault file + normalized derivative).

---

### ADR-005: Orthogonal Multi-Signal Forensic Fusion vs. Monolithic Deep Learning Model

- **Status:** **Approved**
- **Context:** Deep neural networks (e.g., ManTra-Net, TruFor) are popular in recent literature, but require massive GPU VRAM, fail catastrophically out-of-distribution, and behave as opaque black boxes without legal explainability.
- **Decision:** Prioritize a **Multi-Signal Classical Forensic Arsenal** (Error Level Analysis, SIFT Copy-Move Clustering, Noise Inconsistency, Edge Gradient Variance, and EXIF Verification), combining them into a calibrated Consensus Suspicion Mask.
- **Alternatives Considered:**
  1. *Sole reliance on deep learning:* Rejected due to local laptop hardware limitations, brittle PyTorch/CUDA dependencies, and non-explainability during viva defense.
- **Consequences & Trade-offs:**
  - *Positive:* 100% deterministic, explainable, lightweight (< 1.5 s total CPU execution), and fully defensible from first physical principles.
  - *Negative:* Deep learning semantic context is deferred to optional future plugin modules.

---

### ADR-006: SQLite with Write-Ahead Logging (WAL) for Local Data Persistence

- **Status:** **Approved**
- **Context:** The application requires a database to store case metadata, evidence manifests, RoI annotations, and forensic timeline events.
- **Decision:** Utilize **SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL`)**.
- **Alternatives Considered:**
  1. *PostgreSQL / MySQL:* Requires installing, configuring, and running an external database daemon, complicating student and examiner evaluation.
  2. *Flat JSON files:* Lacks relational integrity, concurrent write safety, and transactional ACID guarantees.
- **Consequences & Trade-offs:**
  - *Positive:* Single-file database (`storage/qtrace.db`); zero setup; WAL mode allows concurrent background analysis reads while writing timeline events.
  - *Negative:* Not designed for multi-server horizontal scaling (irrelevant for a local desktop workstation).

---

### ADR-007: Passive C2PA Provenance Extraction without Hard Signing Dependencies

- **Status:** **Approved**
- **Context:** C2PA (Coalition for Content Provenance and Authenticity) is the emerging standard for digital credentials. Full re-signing requires commercial X.509 certificates and hardware security modules.
- **Decision:** Implement **Passive C2PA JUMBF Manifest Extraction and Verification**: The metadata parser inspects uploaded images for C2PA boxes, validates existing certificate chains if present, and logs the findings without requiring Q-TRACE to act as an issuing certificate authority.
- **Alternatives Considered:**
  1. *Self-signed C2PA re-signing:* Triggers untrusted certificate warnings in standard viewers.
  2. *Ignoring C2PA entirely:* Misses a major modern industry provenance advancement.
- **Consequences & Trade-offs:**
  - *Positive:* Full visibility into authentic content credentials when present; zero licensing cost or certificate maintenance burden.

---

### ADR-008: Pure-Python ReportLab Engine for Deterministic PDF Generation

- **Status:** **Approved**
- **Context:** The system must generate professional, court-admissible forensic dossiers containing case metadata, side-by-side evidence images, heatmaps, quantum circuit diagrams, and examiner notes.
- **Decision:** Implement the reporting pipeline using **ReportLab (pure Python)**.
- **Alternatives Considered:**
  1. *WeasyPrint / Headless Chrome (Puppeteer):* Heavy, platform-sensitive dependencies; requires installing GTK or full Chromium binaries on Windows.
  2. *Client-side `window.print()`:* Non-deterministic pagination and browser-dependent layout rendering.
- **Consequences & Trade-offs:**
  - *Positive:* Millimeter-precise layout control; pure Python dependency; deterministic PDF byte output with embedded SHA-256 verification stamps.
  - *Negative:* Requires manual coordinate-based styling instead of standard CSS web styles.

---

### ADR-009: Standard 1024-Shot Measurement Budget for Complete Spatial Reconstruction

- **Status:** **Approved**
- **Context:** In NEQR quantum difference circuits, measurement of position and difference registers collapses the wavefunction to a single pixel per shot.
- **Decision:** Set the **default shot budget to $S = 1024$**, while exposing an interactive slider ($16 \dots 4096$) in the UI.
- **Alternatives Considered:**
  1. *Fixed 100 shots:* Under-samples the 16 states, leaving an average of 1–2 pixels unobserved ($P_{complete} \approx 65\%$).
  2. *Infinite / Statevector readout:* Bypasses quantum measurement physics entirely, defeating the academic purpose of the quantum laboratory.
- **Consequences & Trade-offs:**
  - *Positive:* $S = 1024$ provides $P > 99.999\%$ mathematical certainty of complete spatial reconstruction while still faithfully simulating physical quantum shot noise.
  - *Negative:* Takes $\approx 150 \text{ ms}$ on Qiskit Aer compared to instant statevector lookup.

---

### ADR-010: Zero-Cloud, Zero-GPU Local Windows 11 Runtime Execution Guarantee

- **Status:** **Approved**
- **Context:** The project owner develops and demonstrates Q-TRACE on a local Windows 11 machine. University evaluation environments frequently lack internet connectivity and dedicated NVIDIA GPUs.
- **Decision:** Guarantee that **100% of Q-TRACE capabilities execute natively and locally on Windows 11 without requiring internet access or a dedicated GPU**.
- **Alternatives Considered:**
  1. *IBM Quantum Cloud Hardware Backend:* High queue times (minutes to hours); requires active API token and internet access; completely impractical for live viva demonstration.
  2. *CUDA GPU-dependent CV libraries:* Causes immediate crashes if demonstrated on an Intel-only laptop.
- **Consequences & Trade-offs:**
  - *Positive:* Flawless, instantaneous, repeatable demonstration during university presentations regardless of classroom Wi-Fi or hardware.
  - *Negative:* Quantum simulations are bound to CPU-based Aer simulator limits ($\le 18$ qubits).

---

*Continue to `GLOSSARY.md` for standard terminology and definitions.*

