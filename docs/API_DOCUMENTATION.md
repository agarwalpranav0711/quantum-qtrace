# Q-TRACE REST API Specification

**Platform:** Q-TRACE — Quantum-Assisted Digital Image Forensics Platform  
**Version:** 1.0.0 (FastAPI / OpenAPI 3.1.0)  
**Base URL:** `http://localhost:8000/api/v1`  
**Protocol:** HTTP/1.1 REST + JSON (Local Loopback)  

---

## 1. System Health & Diagnostics

### `GET /health`
Returns the operational status of the backend, local database, and Qiskit quantum simulator runtime.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "quantum_backend": "AerSimulator",
  "storage_status": "accessible",
  "timestamp": "2026-11-20T12:00:00Z"
}
```

---

## 2. Case Management (`/cases`)

### `GET /cases`
Retrieves a paginated list of forensic investigation cases.
- **Query Params:** `skip` (int, default: 0), `limit` (int, default: 50), `search` (str, optional)
- **Response `200 OK`:** `List[CaseResponse]`

### `POST /cases`
Creates a new forensic investigation case container.
- **Request Body (`CaseCreate`):**
  ```json
  {
    "title": "CASE-2025-0842-AUTO",
    "description": "Suspicious front fender damage claim with potential clone-stamping.",
    "investigator_id": "EXAMINER-4821",
    "claim_reference": "CLM-991204-USAA",
    "incident_date": "2025-10-14"
  }
  ```
- **Response `201 Created`:** `CaseResponse` with generated `id` (UUIDv4) and `created_at`.

### `GET /cases/{case_id}`
Retrieves full case details including associated evidence IDs and dossier references.

### `PATCH /cases/{case_id}`
Updates case metadata (title, status, notes).

### `DELETE /cases/{case_id}`
Soft-deletes or archives an investigation case.

---

## 3. Evidence Management (`/evidence`)

### `POST /evidence/upload`
Uploads raw forensic image evidence. Ingests file, computes SHA-256 digest, extracts EXIF, and stores under WORM policy.
- **Form Data:**
  - `file`: Binary file stream (`multipart/form-data`)
  - `case_id`: UUIDv4 string
  - `description`: Optional notes string
  - `evidence_tag`: Optional category tag (e.g. `PRIMARY_CLAIM`, `PRE_LOSS_BASELINE`)
- **Response `201 Created`:**
  ```json
  {
    "id": "e4b2d890-3321-4f12-87ba-791b8a914c10",
    "case_id": "c1f7a182-1209-4321-99af-012847a98bc2",
    "filename": "front_bumper_damage.jpg",
    "sha256": "4a5c68b9829471f0088924bcf8856281726a98715bc7291a182910293847561a",
    "file_size": 3491820,
    "mime_type": "image/jpeg",
    "dimensions": { "width": 4032, "height": 3024 },
    "exif_summary": {
      "camera_make": "Apple",
      "camera_model": "iPhone 13 Pro",
      "software": "Photoshop 25.2",
      "capture_time": "2025-10-15T09:22:11"
    },
    "stored_path": "storage/originals/e4b2d890-3321-4f12-87ba-791b8a914c10.jpg",
    "created_at": "2026-11-20T12:05:00Z"
  }
  ```

### `GET /evidence/{evidence_id}`
Retrieves evidence metadata and verification status.

### `GET /evidence/{evidence_id}/download`
Streams raw immutable original evidence file.

### `POST /evidence/{evidence_id}/verify`
Re-hashes the physical file on disk and verifies against recorded SHA-256 in database.
- **Response `200 OK`:**
  ```json
  {
    "evidence_id": "e4b2d890-3321-4f12-87ba-791b8a914c10",
    "verified": true,
    "recorded_sha256": "4a5c68b...",
    "computed_sha256": "4a5c68b...",
    "timestamp": "2026-11-20T12:06:00Z"
  }
  ```

---

## 4. Classical Forensics Suite (`/forensics`)

### `POST /forensics/analyze/{evidence_id}`
Executes the full classical forensics pipeline across the target image.
- **Request Body (Optional Parameters):**
  ```json
  {
    "run_ela": true,
    "ela_quality": 90,
    "run_noise": true,
    "run_copy_move": true,
    "run_cfa": true,
    "run_phash": true
  }
  ```
- **Response `200 OK` (`ForensicAnalysisResult`):**
  ```json
  {
    "analysis_id": "f901823a-bc12-4211-91a0-129038471209",
    "evidence_id": "e4b2d890-3321-4f12-87ba-791b8a914c10",
    "global_anomaly_score": 0.74,
    "techniques": {
      "ela": {
        "score": 0.82,
        "heatmap_url": "/api/v1/forensics/derivatives/ela_f901823a.png",
        "description": "High compression residual variance concentrated on bumper perimeter."
      },
      "noise": {
        "score": 0.68,
        "heatmap_url": "/api/v1/forensics/derivatives/noise_f901823a.png",
        "snr_variance": 4.12
      },
      "copy_move": {
        "score": 0.91,
        "matches_found": 18,
        "overlay_url": "/api/v1/forensics/derivatives/copymove_f901823a.png"
      },
      "cfa": {
        "score": 0.55,
        "pattern_detected": "RGGB",
        "periodicity_score": 0.42
      },
      "perceptual_hash": {
        "phash": "a7b3c2d1e0f49876",
        "ahash": "ffff0000aaaa5555",
        "dhash": "1234567890abcdef"
      }
    },
    "completed_at": "2026-11-20T12:07:30Z"
  }
  ```

---

## 5. Interactive Canvas & ROI Engine (`/canvas`)

### `POST /canvas/roi`
Registers a Region of Interest (ROI) polygon or bounding box.
- **Request Body (`ROICreate`):**
  ```json
  {
    "evidence_id": "e4b2d890-3321-4f12-87ba-791b8a914c10",
    "label": "ROI-01: Front bumper splice boundary",
    "coordinates": {
      "type": "polygon",
      "points": [[120, 340], [280, 340], [290, 480], [110, 470]]
    },
    "examiner_notes": "Significant gradient mismatch against hood panel under ELA.",
    "confidence": "HIGH"
  }
  ```
- **Response `201 Created`:** `ROIResponse`

### `GET /canvas/roi/by-evidence/{evidence_id}`
Returns all examiner ROIs for an evidence item.

---

## 6. Quantum Comparison Engine (`/quantum`)

### `POST /quantum/compare`
Executes quantum state preparation and distance metric calculation between two image micro-patches.
- **Request Body (`QuantumCompareRequest`):**
  ```json
  {
    "patch_a_id": "roi-patch-01",
    "patch_b_id": "roi-patch-02",
    "patch_size": 4,
    "encoding_type": "AMPLITUDE_16Q",
    "shots": 2048,
    "pixels_a": [0.12, 0.45, 0.88, 0.91, 0.14, 0.42, 0.85, 0.90, 0.11, 0.46, 0.89, 0.92, 0.15, 0.43, 0.86, 0.89],
    "pixels_b": [0.13, 0.44, 0.87, 0.90, 0.14, 0.41, 0.84, 0.91, 0.12, 0.45, 0.88, 0.91, 0.16, 0.42, 0.85, 0.88]
  }
  ```
- **Response `200 OK` (`QuantumCompareResponse`):**
  ```json
  {
    "experiment_id": "qexp-7821-4412-990a",
    "fidelity": 0.9984,
    "trace_distance": 0.0382,
    "bhattacharyya_affinity": 0.9979,
    "circuit_depth": 32,
    "qubits_used": 16,
    "classical_reconstruction_psnr": 42.18,
    "execution_time_ms": 142.5,
    "divergence_significant": false
  }
  ```

---

## 7. Forensic Dossiers & Reports (`/dossier`)

### `POST /dossier/generate`
Compiles an official forensic dossier across case findings.
- **Request Body:**
  ```json
  {
    "case_id": "c1f7a182-1209-4321-99af-012847a98bc2",
    "format": "PDF",
    "include_quantum_experiments": true,
    "include_raw_exif": true,
    "examiner_summary": "Classical and quantum analysis corroborates local copy-move tampering on the right front quarter panel."
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "dossier_id": "dos-991204-pdf",
    "download_url": "/api/v1/dossier/download/dos-991204-pdf",
    "sha256": "8f92a104c8b...",
    "page_count": 8,
    "generated_at": "2026-11-20T12:09:00Z"
  }
  ```
