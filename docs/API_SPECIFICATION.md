# Q-TRACE REST API Specification (v1)

## 1. Overview & Interactive Documentation

The Q-TRACE Core API is built on **FastAPI** and provides fully typed, schema-validated REST endpoints. When the backend server is active, interactive documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

Base API URL prefix: `/api/v1`

---

## 2. Standardized Response & Error Envelopes

### 2.1 Success Responses
Standard responses return typed JSON objects or arrays matching the schemas defined below.

### 2.2 Error Envelope (RFC 7807 Inspired)
All client (4xx) and server (5xx) exceptions return a standardized error object:

```json
{
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Case with identifier 'QC-2026-999' not found.",
    "details": {
      "entity_name": "Case",
      "entity_id": "QC-2026-999"
    }
  }
}
```

Standard Error Codes:
- `VALIDATION_ERROR` (422): Malformed payload, invalid patch dimensions, unsupported file magic bytes.
- `ENTITY_NOT_FOUND` (404): Requested Case or Evidence item does not exist.
- `INTEGRITY_VIOLATION` (409): Duplicate case number or hash conflict.
- `SECURITY_VIOLATION` (403): Directory traversal or null-byte injection attempt.
- `QUANTUM_PROCESSING_ERROR` (400): Simulation failure or state preparation error.
- `INTERNAL_SERVER_ERROR` (500): Unhandled exception shielded from client.

---

## 3. Endpoints Reference

### 3.1 Health & System Diagnostics

#### `GET /health` or `GET /api/v1/health`
Returns quick service health status.
- **Response `200 OK`**:
  ```json
  {
    "status": "healthy",
    "version": "0.3.0",
    "project": "Q-TRACE"
  }
  ```

#### `GET /api/v1/system/info`
Detailed diagnostics across database, storage, and quantum simulation backends.
- **Response `200 OK`**:
  ```json
  {
    "status": "operational",
    "project_name": "Q-TRACE",
    "version": "0.3.0",
    "environment": "development",
    "python_version": "3.11.9",
    "platform": "Windows 11",
    "database": {
      "connected": true,
      "dialect": "sqlite",
      "wal_mode": true
    },
    "storage": {
      "root_path": "D:\\WebDev PROJECTS\\quantum qtrace\\storage",
      "accessible": true,
      "directories_verified": true
    },
    "quantum": {
      "qiskit_version": "2.6.2",
      "aer_simulator_available": true,
      "default_backend": "AerSimulator (Statevector / Matrix Product State)"
    }
  }
  ```

---

### 3.2 Case Management

#### `POST /api/v1/cases`
Register a new forensic investigation case.
- **Request Body**:
  ```json
  {
    "case_number": "QC-2026-0001",
    "title": "Front Bumper Claim Investigation",
    "description": "Alleged parking lot impact claim photograph review."
  }
  ```
- **Response `201 Created`**: Returns created `CaseResponse` model.
- **Response `409 Conflict`**: If `case_number` already exists.

#### `GET /api/v1/cases`
List cases with pagination support.
- **Query Parameters**:
  - `page` (integer, default: 1)
  - `page_size` (integer, default: 20, max: 100)
- **Response `200 OK`**:
  ```json
  {
    "items": [
      {
        "id": "e3a8904a-c0e8-4fd3-b8e9-c7bb0bcf77ef",
        "case_number": "QC-2026-0001",
        "title": "Front Bumper Claim Investigation",
        "description": "Alleged parking lot impact claim photograph review.",
        "status": "OPEN",
        "created_at": "2026-11-19T21:00:00Z",
        "updated_at": "2026-11-19T21:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_next": false
  }
  ```

#### `GET /api/v1/cases/{case_id}`
Retrieve complete case details including attached evidence count and examiner notes.
- **Response `200 OK`**: Returns `CaseDetailResponse`.
- **Response `404 Not Found`**: If case does not exist.

#### `PATCH /api/v1/cases/{case_id}`
Update case metadata or status (`OPEN`, `IN_PROGRESS`, `CLOSED`, `ARCHIVED`).
- **Response `200 OK`**: Returns updated `CaseResponse`.

#### `POST /api/v1/cases/{case_id}/notes`
Attach an examiner note or investigative finding to a case.
- **Request Body**:
  ```json
  {
    "author": "Examiner Fox",
    "content": "Observed unnatural edge artifacts along bumper seam.",
    "evidence_id": "optional-uuid"
  }
  ```
- **Response `201 Created`**: Returns created `ExaminerNoteResponse`.

---

### 3.3 Evidence Ingestion & Integrity Auditing

#### `POST /api/v1/cases/{case_id}/evidence`
Upload and securely ingest an evidence photograph under WORM rules.
- **Content-Type**: `multipart/form-data`
- **Form Fields**: `file` (binary image data: JPEG, PNG, TIFF)
- **Response `201 Created`**:
  ```json
  {
    "id": "b9f71c3e-8d2a-4a6c-9f1e-3b5d7e9f1a2b",
    "case_id": "e3a8904a-c0e8-4fd3-b8e9-c7bb0bcf77ef",
    "original_filename": "bumper_photo.png",
    "stored_filename": "a8e9...3f.png",
    "storage_path": "storage/originals/a8e9...3f.png",
    "mime_type": "image/png",
    "file_size": 24580,
    "sha256_hash": "a8e9c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b83f",
    "width": 800,
    "height": 600,
    "status": "VERIFIED",
    "created_at": "2026-11-19T21:05:00Z"
  }
  ```

#### `GET /api/v1/cases/{case_id}/evidence`
List all evidence items attached to a specific case.
- **Response `200 OK`**: Array of `EvidenceResponse` items.

#### `GET /api/v1/evidence/{evidence_id}`
Get metadata for an individual evidence item.
- **Response `200 OK`**: `EvidenceResponse`.

#### `POST /api/v1/evidence/{evidence_id}/verify`
Perform on-demand cryptographic verification of stored evidence against its ingestion SHA-256 digest.
- **Response `200 OK`**: Returns `EvidenceVerifyResponse` reporting `is_intact` boolean and status (`VERIFIED` or `COMPROMISED`).

---

### 3.4 Quantum Image Processing

#### `POST /api/v1/quantum/compare`
Execute a quantum comparison circuit comparing two 4x4 image patches.
- **Request Body**:
  ```json
  {
    "patch_a": [
      [10, 20, 30, 40],
      [50, 60, 70, 80],
      [90, 100, 110, 120],
      [130, 140, 150, 160]
    ],
    "patch_b": [
      [10, 20, 30, 40],
      [50, 60, 70, 80],
      [90, 100, 110, 120],
      [130, 140, 150, 160]
    ],
    "architecture": "16q",
    "shots": 1024
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "architecture": "16q",
    "qubits": 16,
    "depth": 38,
    "gate_count": 68,
    "fidelity": 1.0,
    "reconstructed_diff_map": [
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0]
    ],
    "classical_diff_map": [
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0]
    ],
    "difference_count": 0,
    "coverage_ratio": 1.0,
    "shots_used": 1024,
    "execution_time_ms": 34.5,
    "identical": true
  }
  ```

