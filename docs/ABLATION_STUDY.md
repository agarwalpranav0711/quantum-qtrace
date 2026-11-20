# Q-TRACE: Multi-Technique Forensic Ablation Study

**Document Reference:** `docs/ABLATION_STUDY.md`  
**Classification:** Empirical Scientific Benchmarking  
**Version:** 1.9.0  
**Data Sources:** `results/part9/ablation/ablation_study_summary.json`, `results/part9/ablation/ablation_study_matrix.csv`  

---

## 1. Experimental Objectives

A core scientific question in digital image forensics is whether combining multiple orthogonal analysis techniques yields measurable performance improvements over using individual techniques in isolation.

To quantify this, we executed an ablation study across 9 systematic configurations evaluated over 4 diverse test samples (Splicing, Copy-Move, Noise-Inconsistency, and Clean Authentic Control):
1. **Single Techniques:** ELA alone, Noise alone, CMFD alone.
2. **Pairwise Combinations (Union & Consensus):** ELA+Noise, ELA+CMFD, Noise+CMFD.
3. **Full Multi-Modal Ensemble:** ELA+Noise+CMFD (Union vs Consensus $K \ge 2$).

---

## 2. Empirical Ablation Matrix

| Configuration | Fusion Mode | Mean Forgery Recall | Mean Forgery IoU | Mean Forgery F1-Score | Clean Control False Positive Pixels | Forensic Trade-off Profile |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Single-ELA** | Individual | $0.0473$ | $0.0382$ | $0.0702$ | 1,024 | Sensitive to recompression; prone to edge false alarms. |
| **Single-Noise** | Individual | $0.9003$ | $0.6048$ | $0.7353$ | **0** | High sensitivity on spatial tampering; zero false alarms on clean panel. |
| **Single-CMFD** | Individual | $0.2897$ | $0.0161$ | $0.0308$ | **0** | Highly specific to keypoint duplication; blind to foreign splices. |
| **Pairwise ELA+Noise** | Union | $0.9096$ | $0.5992$ | $0.7290$ | 1,024 | High recall ($91.0\%$), but inherits ELA edge false alarms. |
| **Pairwise ELA+Noise** | Consensus ($K \ge 2$) | $0.3333$ | $0.2552$ | $0.2891$ | **0** | **Complete suppression of false alarms**; filters uncorroborated noise. |
| **Pairwise Noise+CMFD** | Union | **$0.9135$** | $0.5082$ | $0.5986$ | **0** | **Optimal balance:** Highest multi-attack recall with **zero false alarms**. |
| **Full Ensemble** | Union | **$0.9135$** | $0.5082$ | $0.5986$ | 1,024 | Maximum coverage; requires examiner verification of edge bounds. |
| **Full Ensemble** | Consensus ($K \ge 2$) | $0.3333$ | $0.2552$ | $0.2891$ | **0** | **High-confidence core:** Flags only regions corroborated across modalities. |

---

## 3. Scientific Insights & Engineering Recommendations

1. **Orthogonality Matters:** Individual techniques are domain-specific. CMFD cannot detect foreign image splicing without keypoint duplication; ELA cannot detect lossless copy-move duplication; Noise analysis excels at detecting spatial smoothing and retouching. Combining them achieves a peak multi-attack recall of **$91.35\%$**.
2. **False Positive Suppression via Consensus:** While individual ELA generated 1,024 false-positive pixels on high-contrast authentic panel seams, switching to **Consensus Fusion ($K \ge 2$) reduced clean control false alarms to exactly ZERO**.
3. **Recommended Production Pipeline:** Q-TRACE implements a two-tier presentation:
   - **Tier 1 (High Confidence):** Consensus regions ($K \ge 2$) rendered in solid amber/red with elevated priority.
   - **Tier 2 (Investigative Leads):** Single-technique union regions rendered in dashed outlines labeled *Uncorroborated Observation*.

