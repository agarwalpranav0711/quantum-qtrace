# Q-TRACE Classical Forensic Engine API Reference

**Document ID:** `DOC-API-003`  
**Classification:** REST API Interface Specification  
**Version:** 1.0.0 (Part 5 Milestone Deliverable)  
**Author:** Q-TRACE Principal Architecture & Forensics Engineering Team

---

## 1. Overview & Base Route

The Classical Digital Image Forensics API is mounted under:
```
/api/v1
```

All endpoints return standard JSON responses or binary image streams, with typed RFC 7807 problem details envelopes upon error.

---

## 2. Endpoints Summary

| Method | Route | Description | Auth / Access |
| :--- | :--- | :--- | :--- |
| **`GET`** | `/api/v1/forensics/techniques` | Enumerate all registered forensic algorithms & descriptors | Public Read |
| **`POST`** | `/api/v1/evidence/{evidence_id}/analyze` | Execute forensic analysis pipeline against stored evidence | Examiner Write |
| **`GET`** | `/api/v1/evidence/{evidence_id}/analyses` | List historical analysis executions for an evidence item | Examiner Read |
| **`GET`** | `/api/v1/analysis/{analysis_id}` | Retrieve complete findings, metrics, and artifact links | Examiner Read |
| **`GET`** | `/api/v1/analysis/{analysis_id}/artifacts/{artifact_id}/file` | Stream generated forensic artifact binary (PNG) | Cacheable Read |

---

## 3. Endpoint Details & Examples

### 3.1 List Forensic Techniques
**`GET /api/v1/forensics/techniques`**

Returns catalog metadata for all registered forensic analysis techniques.

#### Example Response:
```json
[
  {
    "id": "ela",
    "name": "Error Level Analysis (ELA)",
    "version": "1.0.0",
    "category": "Compression Physics",
    "description": "Re-encodes image at a reference JPEG quality grid (default: 95) and computes localized re-compression error deltas.",
    "supported_formats": ["image/jpeg", "image/png", "image/tiff"],
    "default_parameters": {
      "quality": 95,
      "scale": 15,
      "edge_masking": true,
      "roi_threshold_std": 2.5
    },
    "limitations": [
      "Natural high-contrast edges inherently yield higher DCT residuals.",
      "Repeated uniform re-saving elevates the error floor."
    ]
  }
]
```

---

### 3.2 Execute Forensic Analysis
**`POST /api/v1/evidence/{evidence_id}/analyze`**

Executes the configured analysis pipeline on target evidence. If `techniques` is omitted, all applicable algorithms are run.

#### Example Request Body:
```json
{
  "techniques": ["metadata", "ela", "noise", "copy_move", "statistics", "perceptual_hash", "resampling"],
  "parameters": {
    "ela": {
      "quality": 95,
      "scale": 15
    },
    "noise": {
      "block_size": 16,
      "variance_threshold_sigma": 2.8
    },
    "copy_move": {
      "algorithm": "SIFT",
      "ratio_threshold": 0.68,
      "min_spatial_distance": 35.0
    }
  }
}
```

#### Example Response:
```json
{
  "analysis_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "evidence_id": "541c1412-02ab-4d80-a897-d1687a065d23",
  "case_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "status": "COMPLETED",
  "total_execution_time_ms": 118.4,
  "techniques_run": 7,
  "techniques_succeeded": 7,
  "techniques_failed": 0,
  "techniques_unsupported": 0,
  "overall_status": "POTENTIAL_INDICATOR_DETECTED",
  "consensus_regions": [
    {
      "roi_id": "CONSENSUS-ROI-01",
      "x": 128,
      "y": 96,
      "width": 64,
      "height": 48,
      "score": 0.87,
      "contributing_techniques": [
        "Error Level Analysis (ELA)",
        "Sensor Noise Inconsistency Analysis"
      ],
      "suggested_quantum_patch": [
        [3, 3, 4, 5],
        [3, 12, 14, 5],
        [4, 13, 15, 6],
        [4, 5, 6, 6]
      ]
    }
  ],
  "artifacts": [
    {
      "artifact_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "artifact_type": "ELA_HEATMAP",
      "stored_filename": "ela_9b1deb4d_95q_8a2f1b4c.png",
      "description": "Error Level Analysis visualization enhanced at scale 15x (JPEG Quality 95)",
      "mime_type": "image/png",
      "sha256_hash": "8a2f1b4c9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b"
    }
  ],
  "created_at": "2026-11-19T22:08:35.123456+00:00"
}
```

---

### 3.3 Stream Forensic Artifact File
**`GET /api/v1/analysis/{analysis_id}/artifacts/{artifact_id}/file`**

Returns raw binary image bytes (`image/png`) with strict path traversal validation and HTTP cache control headers (`Cache-Control: public, max-age=3600`).

