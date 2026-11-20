# Q-TRACE — Dataset Research & Synthetic Tampering Protocol

**Document ID:** `DOC-KB-006`  
**Classification:** Experimental Data Specification  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Scope:** Forensic Benchmarks, CarDD Analysis, and Synthetic Insurance Dataset Protocol  

---

## 1. Executive Summary & Critical Discovery

A rigorous investigation into available computer vision and digital image forensics datasets reveals a crucial distinction that must be defended in the university viva:

> **CRITICAL DISCOVERY:**  
> **There is NO public academic dataset specifically dedicated to "Motor Vehicle Insurance Claim Tampering."**  
> Existing datasets in the automotive insurance space (such as **CarDD**) are *Damage Detection* datasets—they contain authentic, untampered photographs of genuine vehicle crashes and broken body panels. Conversely, established image forensics datasets (such as **CASIA**, **CoMoFoD**, and **MICC-F220**) contain general domestic, natural, or architectural splices and copy-moves, but lack vehicle damage scenarios.

To ensure academic rigor, Q-TRACE adopts a two-pronged data strategy:
1. **General Forensic Validation:** Use verified, peer-reviewed general forensics datasets (**CASIA v2.0**, **CoMoFoD**, **MICC-F220**) to benchmark the mathematical accuracy of classical and quantum algorithms against official ground-truth masks.
2. **Domain-Specific Insurance Evaluation:** Engineer **Q-TRACE-AutoDamage-Bench**, a defensible, reproducible synthetic tampering generation protocol that applies controlled physical and digital manipulations to authentic vehicle photographs, accompanied by automated pixel-accurate ground-truth masks.

---

## 2. Comprehensive Survey of Research Datasets

```
+---------------------------------------------------------------------------------------------------+
|                                 FORENSIC DATASET TAXONOMY                                         |
+---------------------------------------------------------------------------------------------------+
|  1. CASIA Tampering Database (v1.0 & v2.0) --> Broad Splicing & Copy-Move                         |
|  2. CoMoFoD (Tralic et al., 2013)          --> Pixel-Perfect Copy-Move with Attacks               |
|  3. MICC-F220 (Amerini et al., 2011)       --> High-Resolution Geometric Keypoint Copy-Move       |
|  4. Columbia Uncompressed Splicing         --> Uncompressed Sensor-Level Splicing                 |
|  5. CarDD (Wang et al., 2023)              --> AUTHENTIC Vehicle Damage (NOT Tampering)           |
+---------------------------------------------------------------------------------------------------+
```

---

### 2.1 CASIA Image Tampering Detection Evaluation Database

- **Creators / Organization:** Jing Dong, Wei Wang, Tieniu Tan — Institute of Automation, Chinese Academy of Sciences (CASIA).
- **Publication Venue:** IEEE China Summit and International Conference on Signal and Information Processing (ChinaSIP 2013).
- **Subsets:**
  - **CASIA v1.0:** 1,701 total images ($384 \times 256$ pixels, JPEG format). 800 authentic, 921 tampered (simple splicing). Uncompressed or light post-processing.
  - **CASIA v2.0:** 12,617 total images ($320 \times 240$ up to $800 \times 600$ pixels, uncompressed TIFF and lossy JPEG). 7,491 authentic, 5,126 tampered. Includes splicing and copy-move with realistic boundary post-processing (blurring, feathering, deformation).
- **Ground-Truth Masks:** CASIA v1.0 lacked standardized binary masks; community-verified pixel-level binary ground-truth masks for CASIA v2.0 are available via research repositories.
- **Licensing & Availability:** Free for academic and educational non-commercial research upon request; widely mirrored in academic repositories.
- **Suitability for Q-TRACE:** **High.** CASIA v2.0 serves as the primary benchmark for verifying Q-TRACE's Error Level Analysis and Noise Inconsistency modules against established literature numbers.

---

### 2.2 CoMoFoD (Copy-Move Forgery Database)

- **Creators / Organization:** Dijana Tralić, Ivan Župančić, Sonja Grgić, Mislav Grgić — University of Zagreb, Croatia.
- **Publication Venue:** 55th International Symposium ELMAR-2013, Zadar, Croatia (2013).
- **Dataset Composition:**
  - 260 forged image sets (5,200 total image variations).
  - Two image resolution categories: **Small** ($512 \times 512$ pixels, 200 sets) and **Large** ($3000 \times 2000$ pixels, 60 sets).
  - Each set provides: (1) Original authentic image, (2) Forged image, (3) Color-coded transformation mask, and (4) **Binary black-and-white ground-truth mask**.
- **Manipulation Types & Stress Attacks:**
  - Copied regions undergo translation, rotation ($1^\circ \text{ to } 180^\circ$), scaling ($0.5\times \text{ to } 2.0\times$), and non-rigid distortion.
  - Systematic post-processing attacks applied to every set: JPEG compression (Quality factors 20, 30, 40, 50, 60, 70, 80, 90, 100), Gaussian noise addition, image blurring, and contrast adjustment.
- **Licensing & Availability:** Publicly accessible via the University of Zagreb Department of Wireless Communications research portal. Free for academic use.
- **Suitability for Q-TRACE:** **Gold Standard for Copy-Move Testing.** Because CoMoFoD provides exact binary masks alongside original-and-forged pairs, it is the ideal dataset for automated unit tests measuring **Intersection over Union (IoU)**, **Precision**, and **F1 Score** in Q-TRACE's SIFT keypoint engine.

---

### 2.3 MICC-F220

- **Creators / Organization:** Irene Amerini, Lamberto Ballan, Roberto Caldelli, Alberto Del Bimbo, Giuseppe Serra — Media Integration and Communication Center (MICC), University of Florence, Italy.
- **Publication Venue:** IEEE Transactions on Information Forensics and Security (TIFS 2011).
- **Dataset Composition:** 220 high-resolution photographic images (110 authentic, 110 tampered with copy-move attacks). Image dimensions range from $722 \times 480$ up to $2048 \times 1536$ pixels.
- **Ground-Truth Masks:** Provided as binary masks and coordinate bounding boxes.
- **Licensing & Availability:** Academic non-commercial license. Publicly available via University of Florence research site.
- **Suitability for Q-TRACE:** **Very High.** Tests affine invariance of SIFT and ORB descriptors under real-world photographic rotations and scale changes.

---

### 2.4 CarDD (Car Damage Detection Dataset)

- **Creators / Organization:** Xinkuang Wang, Wenjing Li, Zhongcheng Wu.
- **Publication Venue:** *IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS)*, 2023.
- **Dataset Composition:** 4,000 high-resolution images (>684k pixels average) containing over 9,000 annotated instances of vehicle damage across 6 categories:
  1. Dent
  2. Scratch
  3. Crack
  4. Glass shatter
  5. Lamp broken
  6. Tire flat
- **Ground-Truth Annotations:** COCO-format instance segmentation polygon masks identifying the damage boundary on the vehicle.
- **Licensing & Availability:** Hosted on GitHub and Hugging Face under non-commercial research terms.
- **CRITICAL APPRAISAL FOR Q-TRACE:**  
  CarDD is an object detection dataset for insurance damage appraisal, **not** an image forensics dataset. Every photo in CarDD is an authentic crash photo. However, CarDD is uniquely valuable to Q-TRACE because it provides high-resolution, segmented, authentic vehicle damage patches that can be harvested to generate realistic synthetic insurance fraud test cases!

---

## 3. Dataset Summary Matrix

| Dataset Name | Primary Purpose | Image Count | Resolution | Manipulation Types | Binary GT Masks? | Role in Q-TRACE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CASIA v2.0** | General Forensics | 12,617 | Mid ($320 \times 240$ to $800 \times 600$) | Splicing & Copy-Move with post-processing | Yes (Community) | Classical ELA and Noise benchmark |
| **CoMoFoD** | Copy-Move Forensics | 5,200 | $512 \times 512$ & $3000 \times 2000$ | Copy-Move with affine & JPEG attacks | **Yes (Official)** | Core CMFD test suite and IoU validation |
| **MICC-F220** | Keypoint Forensics | 220 | High (up to $2048 \times 1536$) | Copy-Move with geometric scaling | Yes (Official) | SIFT/ORB clustering verification |
| **CarDD** | Damage Detection | 4,000 | High (Avg > 684k px) | **Authentic Damage (None)** | Yes (Damage polygons) | Source substrate for synthetic fraud generation |
| **Q-TRACE-AutoDamage-Bench** | Insurance Tampering | 100 sets | Multi-res ($1024 \times 768$ to $1920 \times 1080$) | Splicing, Cloned Dents, Inpainted Wear | **Yes (Pixel-perfect)** | Primary domain-specific evaluation benchmark |

---

## 4. Q-TRACE-AutoDamage-Bench: Synthetic Insurance Tampering Protocol

To evaluate Q-TRACE on insurance fraud without relying on proprietary insurer databases (which are legally restricted due to GDPR and litigation confidentiality), we define the **Q-TRACE-AutoDamage-Bench** protocol.

```
+---------------------------------------------------------------------------------------------------+
|                       Q-TRACE-AutoDamage-Bench GENERATION PIPELINE                                |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ Authentic Clean Vehicle Base Photo ]          [ Segmented Damage Patch from CarDD ]            |
|                     |                                              |                              |
|                     v                                              v                              |
|          +------------------------------------------------------------------+                     |
|          |                 CONTROLLED MANIPULATION GENERATOR                |                     |
|          +------------------------------------------------------------------+                     |
|          | 1. Splicing Attack: Inset damage patch onto pristine panel       |                     |
|          | 2. Copy-Move Attack: Duplicate bumper dent onto quarter panel     |                     |
|          | 3. Inpainting Attack: Erase pre-existing scratch via Telea/NS    |                     |
|          | 4. Post-Processing: Gaussian blur boundary feathering (r=1..3px) |                     |
|          | 5. Recompression: JPEG save at Q=90, 75, 50                      |                     |
|          +------------------------------------------------------------------+                     |
|                     |                                              |                              |
|                     v                                              v                              |
|  [ Tampered Evidence Photo: test_01.jpg ]         [ Ground-Truth Binary Mask: mask_01.png ]       |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

### 4.1 Four Standardized Fraud Scenarios

1. **Scenario A — Spliced Vehicle Damage (25 Sets):**
   - *Base:* Authentic pristine vehicle panel from CC0/open datasets.
   - *Donor:* High-resolution dent or scratch segmented from CarDD.
   - *Operation:* Alpha-blended composite with Poisson seamless cloning.
   - *GT Mask:* Exact binary silhouette of inserted damage pixels ($1 = \text{forged}, 0 = \text{authentic}$).

2. **Scenario B — Cloned Damage / Copy-Move (25 Sets):**
   - *Base:* Authentic damaged vehicle with a single localized door crease.
   - *Operation:* Source dent region copied, translated, scaled by factor $s \in [0.8, 1.2]$, and pasted onto the rear fender.
   - *GT Mask:* Dual-region mask highlighting source and target clones.

3. **Scenario C — Inpainted Pre-Existing Wear (25 Sets):**
   - *Base:* Vehicle exhibiting minor bumper scuffing or rust.
   - *Operation:* Targeted region inpainted using Navier-Stokes PDE interpolation (`cv2.inpaint`), effectively erasing the damage.
   - *GT Mask:* Bounding mask of the erased region.

4. **Scenario D — Dual-Image Reference Comparison (25 Pairs):**
   - *Base Pair:* Aligned pre-loss policy inspection photo and post-incident photo.
   - *Operation:* Controlled pixel-level modification simulating unrecorded changes.
   - *Target:* Fed directly into the reference SSIM comparator and the 16-qubit Quantum Laboratory.

### 4.2 Standard Annotation & Metadata Format

Each benchmark test case is packaged in a deterministic folder structure:
```
benchmarks/autodamage/
  ├── case_001/
  │   ├── authentic.jpg            # Original unaltered photograph
  │   ├── tampered.jpg             # Manipulated photograph submitted as evidence
  │   ├── ground_truth_mask.png    # 8-bit single-channel binary mask (0 or 255)
  │   └── manifest.json            # Machine-readable ground truth metadata
```

Example `manifest.json`:
```json
{
  "case_id": "AD-001",
  "attack_type": "splicing",
  "source_dataset": "CarDD-Instance-482",
  "target_panel": "front_left_fender",
  "manipulation_details": {
    "feather_radius_px": 2,
    "jpeg_save_quality": 85,
    "donor_iso": 400,
    "host_iso": 100
  },
  "metrics_target": {
    "expected_roi_bbox": [420, 310, 150, 95],
    "tampered_pixel_count": 8420
  }
}
```

---

*Continue to `PRODUCT_DESIGN.md` for the UI/UX specifications and design concept explorations.*

