# Q-TRACE Forensic Analysis Pipeline Specification

**Document ID:** `DOC-PIPE-001`  
**Classification:** Pipeline Orchestration & Integration Specification  
**Version:** 1.0.0 (Part 5 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Forensics Engineering Team

---

## 1. Pipeline Execution Lifecycle

The `ForensicPipeline` class (`backend/app/forensics/pipeline.py`) manages the end-to-end execution of classical forensic analysis against stored evidence.

```
+-----------------------------------------------------------------------------------+
|                           PIPELINE EXECUTION PHASES                               |
+-----------------------------------------------------------------------------------+
|  1. Pre-Flight Integrity Verification  --> SHA-256 hash audit on physical WORM file|
|  2. Safe Image Ingestion in RAM       --> Read bytes directly into memory buffer   |
|  3. Technique Enumeration & Dispatch   --> Resolve requested or all applicable tech|
|  4. Isolated Algorithmic Execution    --> Per-technique try/except sandboxing      |
|  5. Consensus RoI Fusion               --> IoU spatial clustering & cross-validation|
|  6. Database & Artifact Persistence   --> Transactional commit of Analysis & Arts  |
|  7. Response Normalization             --> Structured RFC 7807/Pydantic JSON return|
+-----------------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Technical Detail

### Phase 1: Pre-Flight WORM Integrity Audit
Before executing any algorithm, the pipeline computes the streaming SHA-256 digest of the physical file on disk (`evidence.storage_path`) and compares it to the original ingestion hash (`evidence.sha256_hash`):
- If the hashes match, the evidence is certified as intact and execution proceeds.
- If the hashes diverge, the pipeline immediately sets `evidence.status = "COMPROMISED"`, logs a high-severity security alert, and aborts with an `IntegrityException`. An altered file is never analyzed as authentic evidence.

### Phase 2: In-Memory Safe Ingestion
The original file is read into memory as raw bytes (`Path.read_bytes()`). Original files are never opened in write mode, temporary files are never placed in the `originals/` folder, and read-only OS file attributes (`stat.S_IREAD`) remain locked.

### Phase 3: Technique Enumeration & Applicability Guard
The requested technique IDs (or all registered techniques if omitted) are looked up in the `ForensicRegistry`. For each technique, `is_applicable(mime_type, image_bytes)` validates format compatibility:
- If a technique is inapplicable (e.g. ELA on an uncompressed TIFF), it records `status: UNSUPPORTED_INPUT` with an explanatory diagnostic message rather than terminating the run.

### Phase 4: Isolated Algorithmic Execution
Each technique executes independently within its own error boundary:
- Algorithms accept parameters (e.g., JPEG quality, amplification scale, block size, SIFT ratio).
- Generated image artifacts (heatmaps, plots, vector overlays) are committed to `storage/analysis/` via `StorageService.store_file("analysis", filename, bytes)`.
- If an algorithm crashes (e.g., due to OpenCV out-of-memory or corrupt EXIF), the exception is logged, the technique status is recorded as `ANALYSIS_FAILED`, and the pipeline proceeds seamlessly to the remaining algorithms.

### Phase 5: Multi-Signal Consensus Fusion
The pipeline aggregates candidate Regions of Interest (RoIs) from all techniques:
- Overlapping bounding boxes with $\operatorname{IoU} \ge 0.20$ are merged into unified Consensus RoIs.
- Consensus scores are boosted when multiple orthogonal techniques corroborate the anomaly:
  $$S_{consensus} = \min\left(0.99, \bar{S}_{cluster} + 0.15 \times (N_{methods} - 1)\right)$$
- The centroid $4 \times 4$ pixel patch is extracted, quantized to $[0, 15]$, and attached for Quantum Lab verification.

### Phase 6: Transactional Database Persistence
A single atomic database transaction persists:
- One `Analysis` record in the `analyses` table:
  - `id`: Unique UUID
  - `evidence_id`, `case_id`
  - `analysis_type`: `CLASSICAL_FORENSIC_SUITE` or `CLASSICAL_{TECH}`
  - `status`: `COMPLETED`, `PARTIAL_SUCCESS`, or `FAILED`
  - `config_json`: JSON record of parameters
  - `results_json`: Complete structured findings, observations, indicators, and metrics
  - `execution_time_ms`: Total execution duration in milliseconds
- One `Artifact` record per generated file in the `artifacts` table:
  - `analysis_id`: Foreign key link
  - `artifact_type`: `ELA_HEATMAP`, `NOISE_HEATMAP`, `CMFD_MATCHES`, `HISTOGRAM_PLOT`, `EDGE_GRADIENT_MAP`
  - `file_path`: Path on disk
  - `stored_filename`: Content-addressed filename
  - `sha256_hash`: Hash of generated artifact file

