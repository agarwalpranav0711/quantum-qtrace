# Q-TRACE Dossier & Report Engine: REST API Specification

## 1. Overview & Base URL

The Dossier and Report Generation API provides comprehensive programmatic access for managing forensic investigation dossiers, configuring reporting scopes, generating compiled document previews, and triggering immutable, cryptographically hashed PDF and JSON exports.

- **Base URL**: `/api/v1`
- **Protocol**: HTTP/1.1 or HTTP/2
- **Data Exchange Format**: JSON (`application/json`)
- **Binary Exports**: PDF (`application/pdf`)
- **Authentication**: Local-first workstation mode (ready for Bearer token integration in networked enterprise configurations)

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/cases/{case_id}/dossiers` | Create a new investigation dossier with standard 13-section template |
| `GET` | `/cases/{case_id}/dossiers` | List all dossiers created under a specific case |
| `GET` | `/dossiers/{dossier_id}` | Retrieve dossier details, including ordered section configs |
| `PATCH` | `/dossiers/{dossier_id}` | Update dossier title, examiner, conclusion, or scope |
| `DELETE` | `/dossiers/{dossier_id}` | Permanently delete an un-exported or draft dossier |
| `PATCH` | `/dossiers/{dossier_id}/sections/{section_id}` | Update section title, order, inclusion, or custom content |
| `GET` | `/dossiers/{dossier_id}/preview` | Compile and return live structured dossier preview |
| `POST` | `/dossiers/{dossier_id}/export/pdf` | Generate immutable multi-page PDF, hash SHA-256, and freeze version |
| `POST` | `/dossiers/{dossier_id}/export/json` | Generate open structured JSON, hash SHA-256, and freeze version |
| `GET` | `/dossiers/{dossier_id}/exports` | List all historical export records for a dossier |
| `GET` | `/dossiers/{dossier_id}/exports/{export_id}/file` | Stream exported file with cryptographic verification headers |

---

## 3. Endpoint Specifications

### 3.1 Create Dossier
`POST /api/v1/cases/{case_id}/dossiers`

Creates a new dossier record pre-populated with 13 standard forensic sections.

#### Request Body
```json
{
  "title": "Vehicle Collision Damage Investigation Dossier",
  "examiner_name": "Dr. E. Vance, CFE, EnCE",
  "examiner_title": "Senior Forensic Evidence Analyst",
  "organization": "State Forensic Laboratory / Q-TRACE Unit",
  "executive_summary": "Initial forensic screening of claim photographs indicates localized anomalies.",
  "conclusion": "Pending comprehensive multi-band image analysis."
}
```

#### Response (`201 Created`)
```json
{
  "id": "97e6e584-c6a1-43fd-88ba-1ec52cbb7169",
  "case_id": "18f3a39e-2dc9-46e3-82a9-0648c66eefec",
  "title": "Vehicle Collision Damage Investigation Dossier",
  "examiner_name": "Dr. E. Vance, CFE, EnCE",
  "examiner_title": "Senior Forensic Evidence Analyst",
  "organization": "State Forensic Laboratory / Q-TRACE Unit",
  "executive_summary": "Initial forensic screening of claim photographs indicates localized anomalies.",
  "conclusion": "Pending comprehensive multi-band image analysis.",
  "version": 1,
  "created_at": "2026-11-19T18:20:00.000000Z",
  "updated_at": "2026-11-19T18:20:00.000000Z",
  "sections": [
    {
      "id": "10d65ff9-a1b2-...",
      "dossier_id": "97e6e584-...",
      "section_type": "executive_summary",
      "title": "Executive Summary",
      "sort_order": 1,
      "is_included": true,
      "custom_content": null
    },
    ...
  ]
}
```

---

### 3.2 List Dossiers for Case
`GET /api/v1/cases/{case_id}/dossiers`

#### Response (`200 OK`)
Returns array of `DossierResponse` items.

---

### 3.3 Get Dossier
`GET /api/v1/dossiers/{dossier_id}`

#### Response (`200 OK`)
Returns single `DossierResponse` with full list of sections sorted by `sort_order`.

---

### 3.4 Update Dossier Section
`PATCH /api/v1/dossiers/{dossier_id}/sections/{section_id}`

Allows modifying section title, inclusion flag, sort position, or examiner override content.

#### Request Body
```json
{
  "title": "Executive Summary (Updated for Court Submission)",
  "sort_order": 1,
  "is_included": true,
  "custom_content": "Revised summary incorporating additional quantum difference metric findings."
}
```

#### Response (`200 OK`)
Returns updated `DossierSectionItem`.

---

### 3.5 Get Compiled Dossier Preview
`GET /api/v1/dossiers/{dossier_id}/preview`

Dynamically compiles case evidence, active ROIs, homography comparisons, quantum simulation records, and customized sections into a single structured snapshot ready for frontend inspection or PDF translation.

#### Response (`200 OK`)
```json
{
  "dossier_id": "97e6e584-c6a1-43fd-88ba-1ec52cbb7169",
  "case_id": "18f3a39e-2dc9-46e3-82a9-0648c66eefec",
  "version": 1,
  "generated_at": "2026-11-19T18:25:00.000000Z",
  "case_metadata": {
    "case_number": "QC-2026-CLAIM-9041",
    "title": "Frontal Bumper Collision Claim",
    "examiner": "Dr. E. Vance, CFE, EnCE",
    "created_at": "2026-11-19T17:00:00.000000Z"
  },
  "sections": [ ... ],
  "evidence_register": [
    {
      "id": "e812b...",
      "original_filename": "bumper_damage_left.jpg",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "file_size": 2490123,
      "width": 3840,
      "height": 2160,
      "mime_type": "image/jpeg"
    }
  ],
  "findings": {
    "facts": [ ... ],
    "observations": [ ... ],
    "indicators": [ ... ],
    "hypotheses": [ ... ]
  },
  "rois": [
    {
      "id": "roi-1...",
      "classification": "suspect_clone",
      "confidence": 0.88,
      "crop_artifact_url": "/api/v1/artifacts/roi-crop-1.png",
      "field_notes": "Texture duplication identified across panel seams."
    }
  ],
  "comparisons": [ ... ],
  "quantum_simulations": [ ... ]
}
```

---

### 3.6 Export Dossier PDF
`POST /api/v1/dossiers/{dossier_id}/export/pdf`

Compiles the dossier story via ReportLab, applies two-pass dynamic pagination (`Page X of Y`), computes SHA-256 over raw file output bytes, freezes the version in `dossier_exports`, and increments the dossier version number.

#### Response (`200 OK`)
```json
{
  "id": "exp-a1b2c3d4-...",
  "dossier_id": "97e6e584-c6a1-43fd-88ba-1ec52cbb7169",
  "version": 1,
  "format": "pdf",
  "file_path": "storage/reports/DOS-QC-DOS-A303E67F-01_v1.pdf",
  "sha256_hash": "34593adaaff385baf2ad32f160258309755b25de5119bfc3feca5ae59816e9db",
  "file_size_bytes": 9292,
  "exported_at": "2026-11-19T18:22:45.102394Z",
  "download_url": "/api/v1/dossiers/97e6e584-.../exports/exp-a1b2c3d4-.../file"
}
```

---

### 3.7 Export Dossier Open JSON
`POST /api/v1/dossiers/{dossier_id}/export/json`

Compiles the structured dossier snapshot, exports it to UTF-8 formatted JSON in `storage/reports/`, hashes output bytes with SHA-256, and records the frozen version.

#### Response (`200 OK`)
Returns `DossierExportResponse` with `format: "json"`.

---

### 3.8 List Dossier Exports
`GET /api/v1/dossiers/{dossier_id}/exports`

Returns all historical export records for this dossier, sorted chronologically descending.

#### Response (`200 OK`)
```json
[
  {
    "id": "exp-2...",
    "dossier_id": "97e6e584-...",
    "version": 2,
    "format": "pdf",
    "file_path": "storage/reports/DOS-QC-DOS-A303E67F-01_v2.pdf",
    "sha256_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    "file_size_bytes": 147291,
    "exported_at": "2026-11-19T18:30:10.000000Z",
    "download_url": "/api/v1/dossiers/97e6e584-.../exports/exp-2.../file"
  },
  {
    "id": "exp-1...",
    "dossier_id": "97e6e584-...",
    "version": 1,
    "format": "pdf",
    "file_path": "storage/reports/DOS-QC-DOS-A303E67F-01_v1.pdf",
    "sha256_hash": "34593adaaff385baf2ad32f160258309755b25de5119bfc3feca5ae59816e9db",
    "file_size_bytes": 9292,
    "exported_at": "2026-11-19T18:22:45.000000Z",
    "download_url": "/api/v1/dossiers/97e6e584-.../exports/exp-1.../file"
  }
]
```

---

### 3.9 Download Exported File
`GET /api/v1/dossiers/{dossier_id}/exports/{export_id}/file`

Streams the physical file from disk to the client.

#### Response Headers
- `Content-Type`: `application/pdf` (or `application/json`)
- `Content-Disposition`: `attachment; filename="DOS-QC-DOS-A303E67F-01_v1.pdf"`
- `X-Report-SHA256`: `34593adaaff385baf2ad32f160258309755b25de5119bfc3feca5ae59816e9db`
- `X-Report-Version`: `1`

#### Error Responses
- `404 Not Found`: Export record does not exist or physical file missing from disk.
- `400 Bad Request`: Dossier ID mismatch.

