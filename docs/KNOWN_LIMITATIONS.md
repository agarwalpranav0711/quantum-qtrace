# Q-TRACE Known Technical & Operational Limitations

## 1. Scientific & Quantum Limitations

1. **No Quantum Advantage Claimed**: Quantum Image Processing (QIP) algorithms in Q-TRACE are simulated on a classical CPU using IBM Qiskit Aer. Classical XOR execution is $\sim 2,780\times$ faster than quantum simulation. Q-TRACE demonstrates algorithmic validity, state preparation, and measurement collapse dynamics, but does not provide computational speedup on classical hardware.
2. **Patch Size Restriction**: Quantum simulation is constrained to $4 \times 4$ (or $8 \times 8$) pixel micro-patches. Full-image quantum statevector simulation is classically intractable due to exponential Hilbert space dimensionality ($2^{16} = 65,536$ amplitudes for 16 qubits vs $2^{48}$ for a full megapixel image).
3. **Measurement Sampling Bounds (Coupon Collector)**: Because quantum states collapse upon measurement, obtaining the full difference map requires repeated circuit sampling ($S \ge 155$ shots for 99.9% complete coverage of 16 spatial coordinates). Unobserved pixels are designated as `-1` (unobserved) and never misclassified as zero.

---

## 2. Classical Forensic Limitations

1. **Non-Deterministic Fraud Declaration**: Q-TRACE is an objective decision-support workstation, not an autonomous fraud judge. A high ELA residual or noise inconsistency does not automatically prove malicious fraud; it may stem from legitimate camera firmware post-processing, social media compression, or lighting artifacts.
2. **SIFT Keypoint Sparsity on Featureless Surfaces**: Homography alignment relies on distinctive textural features (corners, edges). On smooth, featureless car surfaces (clean white doors or solid paint), SIFT finds insufficient inliers, causing the alignment engine to fall back to identical-grid pixel matching.
3. **JPEG Multiple Re-compression Degradation**: Multiple successive JPEG compressions (e.g., repeatedly sharing via messaging apps) attenuate high-frequency DCT coefficients, reducing ELA sensitivity.

---

## 3. Storage & Deployment Boundaries

1. **Local-First Architecture**: Q-TRACE is designed for single-examiner workstation use on Windows. While SQLite in WAL mode handles concurrent readers, it is not an enterprise multi-tenant distributed database.
2. **NTFS WORM Emulation**: File immutability is enforced via NTFS file permissions (`stat.S_IREAD`) and application-layer cryptographic verification. It is not hardware-level optical WORM storage.
3. **No Digital Signature Keys**: PDF and JSON exports feature raw binary SHA-256 cryptographic digests and frozen state snapshots. They do not currently include PKI X.509 digital certificates or cryptographic signing keys.

