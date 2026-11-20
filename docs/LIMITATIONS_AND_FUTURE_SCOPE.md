# Q-TRACE Scientific Limitations & Future Research Scope

**Platform:** Q-TRACE — Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform  
**Version:** 1.0.0  
**Transparency Commitment:** Candid, scientifically rigorous disclosure of technical boundaries, simulation constraints, and future engineering roadmaps  

---

## 1. Explicit Scientific Boundaries & Non-Claims

In digital forensics and quantum information science, clear articulation of technical boundaries is essential for courtroom defensibility and academic integrity:

1. **No Automated Fraud Determinations:**
   Q-TRACE is a decision-support platform, not an automated adjudicator. No single metric (high ELA variance, low quantum fidelity, or noise discontinuity) proves intentional fraud. Anomalies may stem from multi-pass social media re-saving, aggressive OEM computational photography (HDR, Night Mode), camera software updates, or physical vehicle surface variations (partial repainting, waxing, dirt).
2. **No Quantum Algorithmic Speedup Claim:**
   The current quantum comparison module executes on classical CPU-based statevector simulators (Qiskit Aer). Simulating quantum state spaces on classical hardware scales exponentially ($\mathcal{O}(2^n)$), which is computationally slower than direct classical array arithmetic. The quantum module's contribution is its **representational geometry** (probability distributions and phase sensitivity in Hilbert space), not classical computational acceleration.
3. **Micro-Patch Scope:**
   Quantum state preparation is currently restricted to $4 \times 4$ ($16$ amplitudes / 4 qubits) and $8 \times 8$ ($64$ amplitudes / 6 qubits) micro-patches. Full-frame gigapixel quantum image processing remains physically impossible on current noisy intermediate-scale quantum (NISQ) hardware.

---

## 2. Technical Limitations of Classical Forensics Modules

1. **Compression Floor Degradation ($Q < 60$):**
   When claim images have undergone aggressive multi-pass compression (e.g., transmitted via WhatsApp or SMS with quality factor $< 60$), high-frequency sensor noise and subtle demosaicing artifacts are obliterated, leading to increased false negatives in noise and CFA modules.
2. **Generative Inpainting and Diffusion Models:**
   State-of-the-art latent diffusion inpainting models (e.g., Stable Diffusion, Midjourney) synthesize statistically coherent noise patterns that can occasionally bypass classical spatial noise variance filters.
3. **Geometric Transformations in Copy-Move:**
   While SIFT/ORB keypoint matching handles standard rotation and scaling, heavily distorted, shear-transformed, or non-linearly warped clone-stamps on curved vehicle body panels may evade keypoint clustering.

---

## 3. Quantum Simulation Limitations

1. **Classical Simulation Overhead:**
   Simulating quantum circuits on CPU introduces memory and latency overhead. Reconstructing full density matrices via tomographic inversion across 64 basis states takes $\sim 1.4\text{ seconds}$ per patch pair, limiting high-throughput batch comparisons.
2. **State Preparation Gate Depth:**
   Exact amplitude encoding requires $\mathcal{O}(2^n)$ CNOT operations. On physical NISQ devices, two-qubit gate error rates ($> 0.5\%$) would cause substantial decoherence without quantum error mitigation.

---

## 4. Future Research & Development Roadmap

```
[Phase 1: Local Foundation (v1.0.0)]
  ├── WORM Storage & SHA-256 Sealing
  ├── 6-Filter Classical Pipeline
  ├── CPU-Simulated Quantum Micro-Patch Comparison
  └── Multi-Page PDF Forensic Dossier Generation
           │
           ▼
[Phase 2: Advanced Deep Learning & Generative Detection]
  ├── Integration of Vision Transformer (ViT) splice localization
  ├── Diffusion residual frequency analysis
  └── Auto-segmentation of vehicle panels (hood, door, bumper, glass)
           │
           ▼
[Phase 3: Hardware-Accelerated QPU Execution]
  ├── IBM Quantum Experience / Braket QPU dispatch integration
  ├── Zero-Noise Extrapolation (ZNE) error mitigation
  ├── Quantum Kernel Methods for patch classification
  └── Blind quantum evidence comparison protocol
```

### Specific Future Enhancements
- **Automated Vehicle Part Segmentation:** Utilizing lightweight local ONNX models to automatically isolate bumpers, headlights, and windshields into structured forensic ROIs.
- **Physical QPU Hardware Dispatch:** Adding optional authenticated API connectors to execute micro-patch fidelity circuits on physical IBM Quantum superconducting processors with readout error mitigation.
- **Expanded Video Forensics:** Extending the pipeline to analyze temporal frame-to-frame compression discontinuities in dashcam collision footage.

