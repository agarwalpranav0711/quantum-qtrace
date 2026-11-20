# Q-TRACE: Mathematical Forensic Evaluation Metrics

**Document Reference:** `docs/FORENSIC_METRICS.md`  
**Classification:** Scientific Methodology & Mathematical Formulations  
**Version:** 1.9.0  

---

## 1. Pixel-Level Confusion Matrix Definitions

In forensic image validation, evaluation occurs at the binary pixel level comparing an algorithmic prediction mask $P(x, y) \in \{0, 1\}$ against the ground-truth tampering mask $G(x, y) \in \{0, 1\}$ across spatial coordinates $(x, y) \in [0, W-1] \times [0, H-1]$:

$$TP = \sum_{x, y} [G(x, y) = 1 \land P(x, y) = 1]$$
$$FP = \sum_{x, y} [G(x, y) = 0 \land P(x, y) = 1]$$
$$FN = \sum_{x, y} [G(x, y) = 1 \land P(x, y) = 0]$$
$$TN = \sum_{x, y} [G(x, y) = 0 \land P(x, y) = 0]$$

---

## 2. Derived Scientific Metrics

### 2.1 Precision (Positive Predictive Value)
$$\text{Precision} = \frac{TP}{TP + FP + \epsilon}$$
*Forensic Meaning:* The proportion of flagged pixels that were genuinely manipulated. High precision ensures investigators do not waste hours scrutinizing authentic vehicle areas.

### 2.2 Recall (Sensitivity / True Positive Rate)
$$\text{Recall} = \frac{TP}{TP + FN + \epsilon}$$
*Forensic Meaning:* The proportion of manipulated pixels successfully enclosed within candidate forensic regions.

### 2.3 F1-Score (Harmonic Mean)
$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall} + \epsilon}$$

### 2.4 Specificity (True Negative Rate)
$$\text{Specificity} = \frac{TN}{TN + FP + \epsilon}$$
*Forensic Meaning:* The accuracy with which authentic unmanipulated background pixels are left unflagged. In digital evidence, maintaining $\text{Specificity} > 0.95$ is vital to avoid false accusations.

### 2.5 Intersection-over-Union (IoU / Jaccard Index)
$$\text{IoU} = \frac{|P \cap G|}{|P \cup G|} = \frac{TP}{TP + FP + FN + \epsilon}$$
*Forensic Meaning:* Strict measure of spatial overlap. Because bounding boxes contain padding around irregular damage contours, typical forensic IoU values range from $0.20$ to $0.65$.

