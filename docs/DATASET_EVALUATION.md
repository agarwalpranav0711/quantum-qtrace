# Q-TRACE: Dataset Evaluation & Synthetic Benchmark Protocol

**Document Reference:** `docs/DATASET_EVALUATION.md`  
**Classification:** Research Methodology & Dataset Governance  
**Version:** 1.9.0  

---

## 1. Evaluation of Existing Forensic & Vehicular Datasets

To establish rigorous scientific validation, we conducted a systematic evaluation of candidate datasets across academia and the automotive insurance domain:

### 1.1 CASIA Image Tampering Dataset (v1.0 & v2.0)
- **Domain:** General photographic splicing and copy-move.
- **Evaluation:** Highly respected academic benchmark with ground-truth binary masks. However, CASIA contains generic nature and indoor photographs, not vehicular insurance damage claims. Additionally, strict academic redistribution licenses restrict packaging within local-first software repositories.

### 1.2 CoMoFoD Copy-Move Forgery Dataset
- **Domain:** Keypoint and block-based copy-move tampering.
- **Evaluation:** Contains 5,000 manipulated images with post-processing (JPEG compression, blur, noise). Provides strong ground truth, but focuses almost exclusively on copy-move tampering without compression splicing or metadata telemetry.

### 1.3 CarDD (Car Damage Detection Dataset)
- **Domain:** Motor-vehicle collision damage object detection.
- **Evaluation:** Crucial finding: **CarDD is an object detection dataset (detecting dents, scratches, broken glass in genuine accidents), NOT an image tampering or forgery dataset.** The images in CarDD are unmanipulated photographic records of damaged vehicles. Using CarDD as a forgery benchmark would produce a complete mismatch between ground truth and forensic detection.

---

## 2. The Q-TRACE Controlled Synthetic Benchmark Protocol

Because genuine insurance claim fraud imagery is strictly confidential (protected by insurer non-disclosure agreements, customer PII, and ongoing litigation), and public datasets lack vehicular domain specificity, Q-TRACE establishes a **reproducible procedural synthetic benchmark suite** (`experiments/part9/run_classical_benchmark.py`).

### Procedural Generation Protocol:
1. **Pristine Base Generation:** Procedurally generates high-texture metallic automotive body panels using harmonic gradient fields combined with Gaussian sensor noise modeling metal flake paint textures.
2. **Deterministic Tampering Ingestion:**
   - **Splicing:** Inserts foreign patches with controlled compression differentials ($Q_1 = 95$ vs $Q_2 = 40$) and foreign chromatic profiles.
   - **Copy-Move:** Duplicates high-entropy feature patches (dents, scratches) with known Euclidean displacement vectors.
   - **Noise Tampering:** Applies localized smoothing or additive noise to simulate digital retouching.
3. **Exact Pixel Ground-Truth Masks:** Generates bit-accurate binary masks ($M(x, y) \in \{0, 1\}$) allowing mathematically exact calculation of True Positives, False Positives, False Negatives, and True Negatives.
4. **Reproducibility Guarantee:** All benchmark scripts use deterministic pseudo-random seeds (`np.random.default_rng(42)`), ensuring identical byte-for-byte image generation across any execution environment.

