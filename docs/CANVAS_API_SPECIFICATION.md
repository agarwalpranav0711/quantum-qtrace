# Canvas and ROI Management REST API Specification

**Document ID**: `DOC-PART6-008`  
**Classification**: Backend Interface Specification  
**Version**: `1.0.0`  
**Status**: `ACTIVE / PRODUCTION`  
**Base URL**: `/api/v1`

---

## 1. Overview

The Canvas and ROI Management API provides endpoints for interactive Region of Interest creation, spatial geometry updates, lossless sub-region cropping, derivative artifact streaming, and automated feature-aligned image comparison.

---

## 2. Endpoints Summary

| Method | Endpoint | Description | Auth / Role |
|:---|:---|:---|:---|
| `POST` | `/evidence/{evidence_id}/rois` | Create a new Region of Interest. | Investigator |
| `GET` | `/evidence/{evidence_id}/rois` | List all ROIs associated with an evidence item. | Investigator |
| `GET` | `/rois/{roi_id}` | Retrieve details of a specific ROI. | Investigator |
| `PATCH` | `/rois/{roi_id}` | Update geometry or annotations for an ROI. | Investigator |
| `DELETE` | `/rois/{roi_id}` | Delete an ROI. | Investigator |
| `POST` | `/rois/{roi_id}/crop` | Generate lossless cropped derivative artifact. | Investigator |
| `POST` | `/evidence/compare` | Execute SIFT homography comparison & delta metrics. | Investigator |
| `GET` | `/derivatives/{artifact_id}/file` | Stream physical derivative artifact (crop / delta). | Investigator |

---

## 3. Detailed Endpoint Contracts

### 3.1 Create Region of Interest
```http
POST /api/v1/evidence/{evidence_id}/rois HTTP/1.1
Content-Type: application/json

{
  "roi_label": "Bumper Impact Crack",
  "roi_type": "EXAMINER_CREATED",
  "x": 100,
  "y": 150,
  "width": 120,
  "height": 80,
  "color": "#00F2FE",
  "observation": "High-contrast fracture line in bumper plastic.",
  "hypothesis": "Physical impact deformation.",
  "confidence": 0.90,
  "analysis_id": null
}
```

#### Response: `201 Created`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "evidence_id": "c39a8112-92df-424a-9524-850989f66858",
  "analysis_id": null,
  "roi_label": "Bumper Impact Crack",
  "roi_type": "EXAMINER_CREATED",
  "x": 100,
  "y": 150,
  "width": 120,
  "height": 80,
  "color": "#00F2FE",
  "observation": "High-contrast fracture line in bumper plastic.",
  "hypothesis": "Physical impact deformation.",
  "confidence": 0.90,
  "created_at": "2026-11-19T17:15:00Z",
  "updated_at": "2026-11-19T17:15:00Z"
}
```

---

### 3.2 List ROIs for Evidence
```http
GET /api/v1/evidence/{evidence_id}/rois HTTP/1.1
```

#### Response: `200 OK`
```json
[
  {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "evidence_id": "c39a8112-92df-424a-9524-850989f66858",
    "analysis_id": null,
    "roi_label": "Bumper Impact Crack",
    "roi_type": "EXAMINER_CREATED",
    "x": 100,
    "y": 150,
    "width": 120,
    "height": 80,
    "color": "#00F2FE",
    "observation": "High-contrast fracture line in bumper plastic.",
    "hypothesis": "Physical impact deformation.",
    "confidence": 0.90,
    "created_at": "2026-11-19T17:15:00Z",
    "updated_at": "2026-11-19T17:15:00Z"
  }
]
```

---

### 3.3 Update Region of Interest (Geometry or Annotations)
```http
PATCH /api/v1/rois/{roi_id} HTTP/1.1
Content-Type: application/json

{
  "roi_label": "Refined Impact Fracture",
  "width": 130,
  "confidence": 0.95
}
```

#### Response: `200 OK`
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "evidence_id": "c39a8112-92df-424a-9524-850989f66858",
  "analysis_id": null,
  "roi_label": "Refined Impact Fracture",
  "roi_type": "EXAMINER_CREATED",
  "x": 100,
  "y": 150,
  "width": 130,
  "height": 80,
  "color": "#00F2FE",
  "observation": "High-contrast fracture line in bumper plastic.",
  "hypothesis": "Physical impact deformation.",
  "confidence": 0.95,
  "created_at": "2026-11-19T17:15:00Z",
  "updated_at": "2026-11-19T17:18:22Z"
}
```

---

### 3.4 Delete Region of Interest
```http
DELETE /api/v1/rois/{roi_id} HTTP/1.1
```

#### Response: `200 OK`
```json
{
  "success": true,
  "roi_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

### 3.5 Generate Sub-Region Lossless Crop Artifact
```http
POST /api/v1/rois/{roi_id}/crop HTTP/1.1
```

#### Response: `201 Created`
```json
{
  "roi_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "evidence_id": "c39a8112-92df-424a-9524-850989f66858",
  "artifact_id": "a98b1234-58cc-4372-a567-0e02b2c3d001",
  "stored_filename": "crop_f47ac10b-58cc-4372-a567-0e02b2c3d479_629ff194.png",
  "sha256_hash": "629ff194c8ea4ed67e030e817359cf450f87cb2b367481171d89bd93e98d9a1f",
  "crop_x": 100,
  "crop_y": 150,
  "crop_width": 130,
  "crop_height": 80,
  "suggested_quantum_patch": [
    [2, 4, 6, 8],
    [10, 12, 14, 15],
    [1, 3, 5, 7],
    [9, 11, 13, 0]
  ]
}
```

---

### 3.6 Execute Image Comparison
```http
POST /api/v1/evidence/compare HTTP/1.1
Content-Type: application/json

{
  "primary_evidence_id": "c39a8112-92df-424a-9524-850989f66858",
  "comparison_evidence_id": "d48b9223-92df-424a-9524-850989f66899",
  "align_images": true,
  "difference_threshold": 15,
  "manual_offset_x": 0,
  "manual_offset_y": 0
}
```

#### Response: `200 OK`
```json
{
  "primary_evidence_id": "c39a8112-92df-424a-9524-850989f66858",
  "comparison_evidence_id": "d48b9223-92df-424a-9524-850989f66899",
  "identical_dimensions": true,
  "primary_dimensions": { "width": 800, "height": 600 },
  "comparison_dimensions": { "width": 800, "height": 600 },
  "alignment_performed": true,
  "alignment_method": "SIFT_RANSAC_HOMOGRAPHY",
  "alignment_status": "SIFT_HOMOGRAPHY_ALIGNED",
  "transformation_matrix": [
    [1.002, 0.001, -2.4],
    [-0.001, 0.999, 1.2],
    [0.000001, -0.000002, 1.0]
  ],
  "difference_pixel_count": 1420,
  "difference_percentage": 0.295,
  "mean_absolute_error": 2.14,
  "root_mean_square_error": 4.88,
  "psnr_db": 34.37,
  "ssim_score": 0.978,
  "artifact_id": "e77c4455-58cc-4372-a567-0e02b2c3d999",
  "artifact_filename": "diff_c39a8112_d48b9223_1732036500.png",
  "suggested_quantum_patch_a": [
    [0, 8, 8, 0],
    [8, 12, 12, 8],
    [8, 12, 12, 8],
    [0, 8, 8, 0]
  ],
  "suggested_quantum_patch_b": [
    [0, 8, 8, 0],
    [8, 15, 12, 8],
    [8, 12, 12, 8],
    [0, 8, 8, 0]
  ]
}
```

---

### 3.7 Stream Derivative Artifact File
```http
GET /api/v1/derivatives/{artifact_id}/file HTTP/1.1
```

#### Response: `200 OK`
```http
HTTP/1.1 200 OK
Content-Type: image/png
Content-Length: 48921
Cache-Control: public, max-age=31536000, immutable

[Binary PNG Byte Stream]
```

