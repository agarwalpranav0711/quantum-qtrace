# Q-TRACE — Master Technical Glossary & Terminology Index

**Document ID:** `DOC-KB-013`  
**Classification:** Reference Lexicon  
**Version:** 1.0.0 (Part 1 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Research Team  
**Scope:** Quantum Mechanics, Digital Image Forensics, Cryptography, and Software Engineering  

---

## 1. Quantum Mechanics & Quantum Image Processing (QIP)

- **Ancilla Qubit:** An auxiliary, temporary qubit allocated in a quantum circuit to assist in intermediate calculations (such as carrying borrow bits, computing multi-qubit boolean flags, or storing parity) that is either uncomputed back to $|0\rangle$ or measured independently.
- **Basis State:** A state belonging to an orthonormal basis spanning the Hilbert space of a quantum system. In an $n$-qubit system, the computational basis states are the $2^n$ orthogonal vectors $\{|0\rangle, |1\rangle, \dots, |2^n - 1\rangle\}$.
- **Born's Rule:** The fundamental postulate of quantum mechanics stating that the probability $P(i)$ of measuring a quantum state $|\psi\rangle = \sum \alpha_i |i\rangle$ in the computational basis state $|i\rangle$ is equal to the squared modulus of its probability amplitude: $P(i) = |\alpha_i|^2$.
- **Circuit Depth:** The maximum number of gate operations on any single qubit along the longest causal execution path in a quantum circuit, representing the minimal time slices required for parallel execution.
- **CNOT (Controlled-NOT):** A two-qubit unitary gate that inverts the state of a target qubit if and only if the control qubit is in the state $|1\rangle$. In the computational basis: $|c, t\rangle \to |c, t \oplus c\rangle$. It is the fundamental physical building block for reversible bitwise XOR comparison.
- **Coupon Collector's Problem:** A classical probability theorem stating that if each measurement independently yields one of $N$ equally likely outcomes with replacement, the expected number of trials required to collect all $N$ outcomes is $E[T] = N \cdot H_N \approx N \ln N$. In Q-TRACE, it governs how many measurement shots are required to reconstruct a full spatial difference map from a quantum superposition.
- **FRQI (Flexible Representation of Quantum Images):** An amplitude-based quantum image encoding model (Le et al., 2011) that maps pixel gray levels onto the continuous rotation angle $\theta_i$ of a single color qubit: $|I\rangle = \frac{1}{2^n} \sum (\cos\theta_i |0\rangle + \sin\theta_i |1\rangle) \otimes |i\rangle$.
- **Grover's Algorithm:** A quantum search algorithm discovered by Lov Grover (1996) that searches an unstructured database of $N$ items for $M$ marked items in $\mathcal{O}(\sqrt{N/M})$ queries, providing a provable quadratic speedup over classical $\mathcal{O}(N)$ brute-force search.
- **Hadamard Gate ($H$):** A single-qubit unitary gate that transforms computational basis states into equiprobable superposition states: $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$, $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
- **Multi-Controlled NOT ($C^k(NOT)$):** A generalized reversible quantum logic gate that flips a target qubit if and only if all $k$ control qubits are simultaneously in state $|1\rangle$. Used in NEQR state preparation to write pixel intensity values conditioned on spatial coordinates.
- **NEQR (Novel Enhanced Quantum Representation):** A basis-state quantum image representation model (Zhang et al., 2013) that encodes both pixel coordinates and gray-scale intensity values into computational basis states: $|I\rangle = \frac{1}{2^n} \sum |f(Y, X)\rangle |Y\rangle |X\rangle$. It enables direct, reversible algebraic operations on pixel values.
- **NISQ (Noisy Intermediate-Scale Quantum):** The contemporary era of quantum computing characterized by physical processors with 50 to a few hundred noisy, non-fault-tolerant qubits without full quantum error correction.
- **Qiskit Aer:** A high-performance C++ simulator framework within IBM Qiskit that provides realistic statevector, unitary, and shot-based (QasmSimulator) execution of quantum circuits on classical CPUs.
- **Quantum State Tomography:** The process of reconstructing the full density matrix of an unknown quantum state via repeated measurements in multiple non-commuting bases; notoriously expensive in runtime and sample complexity.
- **Shot Count ($S$):** The total number of times an identical quantum circuit is prepared, executed, and measured to collect an empirical frequency distribution over the output basis states.
- **Shot Noise:** The statistical variance in quantum measurement outcomes arising from the fundamental probabilistic nature of quantum collapse, scaling inversely with the square root of the shot budget ($\sigma \propto 1/\sqrt{S}$).
- **Superposition:** The principle of quantum mechanics wherein a quantum state can exist as a linear combination of two or more mutually exclusive basis states: $|\psi\rangle = \alpha |0\rangle + \beta |1\rangle$ with $|\alpha|^2 + |\beta|^2 = 1$.
- **Toffoli Gate ($CCNOT$):** A universal 3-qubit reversible gate that flips the third qubit if and only if the first two qubits are $|1\rangle$.
- **Unitary Transformation:** A linear operator $U$ on a complex Hilbert space satisfying $U^\dagger U = U U^\dagger = I$, preserving vector norm and inner products, representing physically reversible quantum evolution.

---

## 2. Digital Image Forensics & Computer Vision

- **Boundary Feathering:** An image editing technique that smooths or blurs the perimeter of a spliced or inserted object to blend it seamlessly into the background, leaving distinct gradient drops detectable via high-frequency derivative filtering.
- **Connected Components:** An algorithmic graph technique in computer vision that groups adjacent foreground pixels into discrete contiguous blobs, used in Q-TRACE to extract bounding boxes around suspicious regions.
- **Copy-Move Forgery Detection (CMFD):** The identification of malicious tampering wherein a region of an image is duplicated, translated, rotated, or scaled and pasted into another location within the *same* photograph (e.g., duplicating a scratch or dent).
- **Discrete Cosine Transform (DCT):** A mathematical transform expressing a finite sequence of data points in terms of a sum of cosine functions oscillating at different frequencies; foundational to JPEG lossy image compression.
- **Error Level Analysis (ELA):** A digital forensic technique developed by Dr. Neal Krawetz that analyzes the difference between an input lossy image and a version resaved at a known quality factor ($Q=95\%$), exposing regions that possess different compression histories or foreign quantization tables.
- **False Positive Rate (FPR):** The proportion of authentic, unaltered pixels or cases that are incorrectly flagged by an algorithm as suspicious: $FPR = FP / (FP + TN)$.
- **Forensic Patch Tiling:** The architectural methodology developed in Q-TRACE that uses classical computer vision algorithms to identify high-suspicion candidate clusters across a multi-megapixel image, extracting localized $4 \times 4$ or $8 \times 8$ tiles for deep quantum circuit verification.
- **Image Splicing:** A digital forgery technique where a visual element or region from a source donor photograph is copied and pasted into a different host photograph.
- **Inpainting (Content-Aware Fill):** Algorithmic restoration or replacement of missing or selected pixel regions using surrounding texture synthesis or partial differential equation (PDE) interpolation, often used to digitally erase pre-existing vehicle wear or rust.
- **Intersection over Union (IoU / Jaccard Index):** A quantitative metric measuring the spatial overlap accuracy between a predicted suspicious bounding box/mask $A$ and the true ground-truth mask $B$: $\operatorname{IoU} = |A \cap B| / |A \cup B|$.
- **JPEG Ghost Analysis:** A forensic method developed by Dr. Hany Farid that exposes multiple JPEG compressions by analyzing the minimum error displacement curve across varied quality factors.
- **Lowe's Ratio Criterion:** A feature matching threshold in SIFT stating that a candidate keypoint match is accepted only if the distance to the closest neighbor is less than a fraction $\tau$ (typically 0.65–0.75) of the distance to the second-closest neighbor, eliminating ambiguous matches.
- **Noise Variance Inconsistency:** A blind forensic signal analysis method that calculates local high-frequency sensor noise variance across overlapping sub-blocks, identifying foreign splices whose sensor noise floors deviate from the camera's ambient noise.
- **ORB (Oriented FAST and Rotated BRIEF):** A fast, lightweight binary keypoint detector and descriptor developed as an efficient open alternative to SIFT and SURF.
- **Photo-Response Non-Uniformity (PRNU):** A deterministic, unique physical fingerprint left on digital images by microscopic silicon wafer manufacturing imperfections across the camera sensor pixels.
- **Region of Interest (RoI):** A localized spatial sub-region or bounding box within an evidence image that has been flagged as statistically anomalous by one or more forensic algorithms.
- **SIFT (Scale-Invariant Feature Transform):** A computer vision feature extraction algorithm (Lowe, 1999) that detects invariant local extrema across Difference-of-Gaussian scale space and computes 128-dimensional gradient orientation descriptors.
- **Structural Similarity Index (SSIM):** A perceptual metric (Wang et al., 2004) measuring visual degradation between a reference image and a test image based on luminance, contrast, and structural correlation.

---

## 3. Cryptography, Provenance & Evidence Standards

- **C2PA (Coalition for Content Provenance and Authenticity):** An open technical standard established by Adobe, Microsoft, Intel, and Truepic that defines cryptographic protocols for embedding tamper-evident assertions, authorship claims, and edit histories directly inside digital media containers.
- **Chain of Custody:** The chronological, legally defensible documentation showing the custody, control, transfer, analysis, and disposition of digital evidence, ensuring no tampering occurred between acquisition and courtroom presentation.
- **Decision Support System (DSS):** An interactive software platform designed to assist human decision-makers in evaluating complex data, compiling evidence, and identifying patterns, without usurping ultimate human judgment or legal responsibility.
- **EXIF (Exchangeable Image File Format):** A technical metadata standard specifying formats for images, sound, and ancillary tags recorded by digital cameras (camera model, focal length, exposure, GPS coordinates, timestamps, and embedded thumbnails).
- **ISO/IEC 27037:2012:** The international standard providing guidelines for the identification, collection, acquisition, and preservation of digital evidence to maintain its integrity and legal admissibility.
- **JUMBF (JPEG Universal Metadata Box Format):** A modular binary container format (ISO/IEC 19566-5) used to embed structured metadata boxes—such as C2PA provenance manifests—inside JPEG, PNG, and WebP files.
- **SHA-256 (Secure Hash Algorithm 256-bit):** A cryptographic hash function designed by the U.S. National Security Agency (NIST FIPS 180-4) that generates a deterministic, fixed-size 256-bit (32-byte) digest from an arbitrary sequence of bytes. It is computationally infeasible to invert or find collisions.
- **WORM (Write-Once-Read-Many) Storage:** A data storage architecture enforcing that once digital evidence is ingested and written to disk, it cannot be modified, overwritten, or deleted by any application process, preserving pristine original copies.

---

*Continue to `RESEARCH_INDEX.md` for the master document index and viva study guide.*

