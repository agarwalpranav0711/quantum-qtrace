# Q-TRACE: Post-Processing Robustness & Degradation Experiments

**Document Reference:** `docs/ROBUSTNESS_EXPERIMENTS.md`  
**Classification:** Empirical Scientific Benchmarking  
**Version:** 1.9.0  
**Data Sources:** `results/part9/classical/robustness_metrics.csv`  

---

## 1. Experimental Methodology

Digital evidence submitted in insurance claims is rarely preserved in pristine, uncompressed camera-raw format. Claimants frequently recompress, downscale, or send photos through mobile applications.

To evaluate how post-processing degrades forensic detection fidelity, we subjected spliced automotive test cases to a systematic JPEG recompression quality sweep ($Q \in \{50, 70, 85, 95\}$):

```
+-------------------------------------------------------------------------------+
|                    JPEG RECOMPRESSION ROBUSTNESS PROTOCOL                     |
|                                                                               |
|  [Spliced Composite] ---> [JPEG Encode at Quality Q] ---> [Decode & Analyze] |
|        (Q95+Q40)               Q in {50, 70, 85, 95}            (ELA Engine)  |
+-------------------------------------------------------------------------------+
```

---

## 2. Empirical Robustness Results

| Perturbation Setting | Candidate ROIs Detected | Pixel Precision | Pixel Recall | Pixel F1-Score | Pixel IoU | Failure Mode Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **JPEG Quality 95** | 1 | $0.2036$ | $1.0000$ | $0.3383$ | $0.2036$ | Complete retention of foreign compression differential. |
| **JPEG Quality 85** | 1 | $0.2036$ | $1.0000$ | $0.3383$ | $0.2036$ | Residual high-frequency compression differential fully preserved. |
| **JPEG Quality 70** | 1 | $0.2036$ | $1.0000$ | $0.3383$ | $0.2036$ | Quantization table re-aligns high frequencies; boundary remains detectable. |
| **JPEG Quality 50** | 0 | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | Severe global quantization overrides subtle pre-existing compression history. |

---

## 3. Scientific Conclusions on Robustness Boundaries

1. **JPEG Quality Threshold ($Q \ge 70$):** Q-TRACE's ELA engine maintains $100\%$ spatial recall on spliced compression anomalies down to $Q=70$.
2. **Low-Quality Failure ($Q \le 50$):** Heavy recompression wipes out high-frequency DCT residuals across the entire image frame, causing ELA to report no candidate regions.
3. **Engineering Mitigation:** When Q-TRACE detects an image with an average JPEG quality estimate $< 65$, the system automatically emits a technical limitation banner: *"Heavy global recompression detected; subtle compression differentials may have been obliterated."*

