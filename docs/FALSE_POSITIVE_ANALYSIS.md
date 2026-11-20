# Q-TRACE: False Positive Analysis & Mitigation in Vehicular Forensics

**Document Reference:** `docs/FALSE_POSITIVE_ANALYSIS.md`  
**Classification:** Forensic Methodology & Technical Failure Modes  
**Version:** 1.9.0  

---

## 1. Physical Causes of False Forensic Indicators

In digital forensics on motor-vehicle insurance photographs, false alarms are frequent if algorithms are used without domain awareness. Physical factors inherent to automotive photography routinely trigger anomalous measurements in unmanipulated photographs:

```
+-------------------------------------------------------------------------------+
|             COMMON CAUSES OF FALSE POSITIVES IN VEHICLE PHOTOGRAPHY           |
+-------------------------------------------------------------------------------+
| 1. High-Contrast Geometry & Specular Reflection                               |
|    - Chrome bumpers, mirrors, and headlight glass create abrupt luminance     |
|      transitions that produce natural DCT high-frequency ringing in ELA.       |
| 2. Metallic Paint Flakes & Pearlescent Coatings                               |
|    - Modern car coatings contain micro-aluminum flakes, producing localized   |
|      variance spikes that mimic foreign additive sensor noise.                |
| 3. In-Camera Computational Photography & Tone Mapping                         |
|    - Modern smartphones apply multi-frame HDR, deep shadows sharpening, and   |
|      neural de-noising locally, disrupting uniform PRNU noise baselines.       |
| 4. Social Messaging / Cloud Transmission Recompression                        |
|    - Claimants frequently transmit evidence photos via WhatsApp, WeChat, or   |
|      email gateways that aggressively recompress images at Q=70, stripping     |
|      original high-frequency residuals and altering metadata.                 |
+-------------------------------------------------------------------------------+
```

---

## 2. Q-TRACE Mitigation Architecture

To prevent false accusations of fraud, Q-TRACE incorporates four engineering mitigations:

1. **Luminance Edge Masking in ELA:** Suppresses edge ringing by weighting ELA difference maps against the Sobel gradient magnitude of the original image. Pure luminance edges are attenuated, highlighting non-structural compression mismatches.
2. **Median-Filtered Noise Floor Normalization:** Evaluates local noise variance against the interquartile range (IQR) of the entire image rather than a fixed global threshold.
3. **Multi-Signal Spatial Consensus:** Single-technique candidate regions are flagged as *UNCONFIRMED_OBSERVATION*. Only regions corroborated by intersecting physical domains (e.g. ELA anomaly intersecting with noise inconsistency) are elevated to *CONSENSUS_INDICATOR*.
4. **Mandatory Examiner Hypotheses:** The UI prompts the examiner with benign alternate hypotheses (e.g., "Could this ELA variance be caused by specular sunlight on curved metal?") before allowing the finding to be included in a final dossier.

