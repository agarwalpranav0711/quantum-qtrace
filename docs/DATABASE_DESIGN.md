# Q-TRACE Database Design & Data Modeling Specification

## 1. Relational Database Architecture

The Q-TRACE persistence layer utilizes **SQLite 3** operating with **Write-Ahead Logging (WAL)** mode through **SQLAlchemy 2.0+** ORM.

### 1.1 Rationale for SQLite in WAL Mode
For a university research and forensic intelligence platform deployed on a local workstation, SQLite provides compelling advantages over heavy database daemons (PostgreSQL / MySQL):
1. **Zero External Daemon Overhead**: Runs in-process without requiring background services, port binding, or credential management.
2. **ACID Concurrency via WAL (`PRAGMA journal_mode=WAL;`)**:
   - In traditional rollback-journal mode, writers block readers and readers block writers.
   - In WAL mode, changes are written sequentially to a separate `-wal` file. Readers read from the database file and WAL concurrently without locking writers. A single writer can proceed without blocking ongoing investigative reads.
3. **Foreign Key Enforcement (`PRAGMA foreign_keys=ON;`)**:
   - SQLite disables foreign keys by default for backward compatibility. Q-TRACE automatically enforces strict referential integrity on every database connection via an SQLAlchemy `connect` event listener.
4. **Fast Synchronous Commit (`PRAGMA synchronous=NORMAL;`)**:
   - Provides full crash resistance without requiring synchronous disk flushes on every write, improving transaction throughput on solid-state drives.

---

## 2. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    CASES ||--o{ EVIDENCE : "contains (1:N)"
    CASES ||--o{ EXAMINER_NOTES : "has (1:N)"
    CASES ||--o{ ANALYSES : "tracks (1:N)"
    EVIDENCE ||--o{ ANALYSES : "subject of (1:N)"
    EVIDENCE ||--o{ EXAMINER_NOTES : "referenced by (0:N)"
    ANALYSES ||--o{ ARTIFACTS : "produces (1:N)"

    CASES {
        string id PK "UUID string"
        string case_number UK "Unique e.g. QC-2026-001"
        string title "Case Title"
        string description "Case Summary"
        string status "OPEN, IN_PROGRESS, CLOSED, ARCHIVED"
        datetime created_at "UTC Timestamp"
        datetime updated_at "UTC Timestamp"
    }

    EVIDENCE {
        string id PK "UUID string"
        string case_id FK "References cases.id"
        string original_filename "Original uploaded file name"
        string stored_filename "Content-addressed SHA-256 name"
        string storage_path "Physical disk path"
        string mime_type "image/jpeg, image/png, image/tiff"
        integer file_size "Size in bytes"
        string sha256_hash "64-char hexadecimal digest"
        integer width "Pixel width"
        integer height "Pixel height"
        string status "VERIFIED, COMPROMISED, PROCESSING"
        datetime created_at "UTC Timestamp"
    }

    ANALYSES {
        string id PK "UUID string"
        string case_id FK "References cases.id"
        string evidence_id FK "References evidence.id"
        string analysis_type "QUANTUM_COMPARISON_16Q, 12Q, etc."
        string algorithm_name "Algorithm display name"
        string status "PENDING, RUNNING, COMPLETED, FAILED"
        text config_json "Parameters (shots, noise, etc.)"
        text results_json "Fidelity, diff counts, coupon stats"
        float execution_time_ms "Execution duration"
        text error_message "Failure explanation if failed"
        datetime created_at "UTC Timestamp"
    }

    ARTIFACTS {
        string id PK "UUID string"
        string analysis_id FK "References analyses.id"
        string artifact_type "DIFFERENCE_MAP, HEATMAP, CIRCUIT"
        string file_path "Physical disk path"
        string stored_filename "Storage filename"
        string sha256_hash "64-char hexadecimal digest"
        datetime created_at "UTC Timestamp"
    }

    EXAMINER_NOTES {
        string id PK "UUID string"
        string case_id FK "References cases.id"
        string evidence_id FK "Optional reference to evidence.id"
        string author "Investigator name or role"
        text content "Note text observation"
        datetime created_at "UTC Timestamp"
        datetime updated_at "UTC Timestamp"
    }
```

---

## 3. Relational Tables Specification

### 3.1 `cases` Table
Maintains investigative boundaries for claims and incident reviews.
- **Primary Key**: `id` (`VARCHAR(36)` UUID)
- **Unique Key**: `case_number` (`VARCHAR(64)`, Indexed) — human-readable identifier (e.g. `QC-2026-0001`).
- **Fields**: `title`, `description`, `status` (`OPEN`, `IN_PROGRESS`, `CLOSED`, `ARCHIVED`), `created_at`, `updated_at`.
- **Cascade Behavior**: Deletion of a case cascades to all associated notes, evidence items, and analysis records.

### 3.2 `evidence` Table
Preserves digital evidence records, metadata, and cryptographic digests.
- **Primary Key**: `id` (`VARCHAR(36)` UUID)
- **Foreign Key**: `case_id` (`VARCHAR(36)`) references `cases.id` with `ON DELETE CASCADE`.
- **Fields**: `original_filename`, `stored_filename`, `storage_path`, `mime_type`, `file_size`, `sha256_hash` (Indexed), `width`, `height`, `status` (`VERIFIED`, `COMPROMISED`, `PROCESSING`, `ERROR`), `created_at`.
- **Integrity Rule**: `sha256_hash` represents the SHA-256 digest computed at the moment of file ingestion.

### 3.3 `analyses` Table
Tracks algorithmic executions (quantum simulations, classical XOR comparisons, future ELA/noise runs).
- **Primary Key**: `id` (`VARCHAR(36)` UUID)
- **Foreign Keys**:
  - `case_id` references `cases.id` (`ON DELETE CASCADE`)
  - `evidence_id` references `evidence.id` (`ON DELETE CASCADE`)
- **Fields**: `analysis_type`, `algorithm_name`, `status` (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`), `config_json` (Text), `results_json` (Text), `execution_time_ms` (Float), `error_message` (Text), `created_at`.
- **Flexibility**: Storing parameters and output metrics in structured JSON text fields ensures seamless extensibility across different algorithmic families without schema migration churn.

### 3.4 `artifacts` Table
Records derived binary outputs produced by analyses (such as difference maps, heatmaps, and quantum circuit diagrams).
- **Primary Key**: `id` (`VARCHAR(36)` UUID)
- **Foreign Key**: `analysis_id` references `analyses.id` (`ON DELETE CASCADE`).
- **Fields**: `artifact_type`, `file_path`, `stored_filename`, `sha256_hash`, `created_at`.

### 3.5 `examiner_notes` Table
Chronicles investigator observations, audit remarks, and viva presentation notes.
- **Primary Key**: `id` (`VARCHAR(36)` UUID)
- **Foreign Keys**:
  - `case_id` references `cases.id` (`ON DELETE CASCADE`)
  - `evidence_id` references `evidence.id` (`ON DELETE SET NULL`)
- **Fields**: `author`, `content`, `created_at`, `updated_at`.

