# Q-TRACE Security Audit & Defensive Engineering Review

**Classification:** Practical Security Code Review & Forensic Boundary Audit  
**Target Scope:** Local-First Evidence Preservation, API Isolation, and Defensive Input Validation  
**Auditor Notice:** This document represents an architectural and source code security review conducted under Part 8 engineering guidelines. It is not an external penetration test.

---

## 1. File Handling & Storage Security

| Vector | Threat Mechanism | Implemented Defense | Status |
| :--- | :--- | :--- | :--- |
| **Magic-Byte Spoofing** | Attacker renames malicious executable (`payload.exe`) to `claim.jpg`. | Multi-tier validation inspects magic bytes (`\xFF\xD8\xFF` for JPEG, `\x89PNG` for PNG, `II*\x00` / `MM\x00*` for TIFF) via `validate_image_file()`. Fails closed before disk write. | **VERIFIED** |
| **Decompression Bombs** | Highly compressed 10 KB file decompressing to 20 GB in memory (ZIP/PNG bomb). | Pillow `Image.MAX_IMAGE_PIXELS = 67,108,864` (8192x8192 limit) enforced. Memory allocation bounds checked before decoding. | **VERIFIED** |
| **Directory Traversal** | Filename payload `../../etc/passwd` or `..\..\Windows\System32\malicious.dll`. | `resolve_safe_path()` resolves target path and strictly verifies `resolved.is_relative_to(category_dir)`. Rejects any path escape. | **VERIFIED** |
| **Evidence Mutation** | Subsequent edit or malware overwriting original image bitstream. | `store_original()` applies `stat.S_IREAD` read-only permissions on Windows NTFS. File is content-addressed by SHA-256 digest. | **VERIFIED** |
| **Deduplication Collisions** | Attacker uploads altered file with duplicate name. | Content-addressing checks SHA-256 and byte length. If hash matches existing file with different size, raises `INTEGRITY_VIOLATION`. | **VERIFIED** |

---

## 2. API Security & Input Shielding

| Vector | Threat Mechanism | Implemented Defense | Status |
| :--- | :--- | :--- | :--- |
| **SQL Injection** | SQL fragments in search queries or case numbers (`' OR 1=1--`). | 100% parameterized queries via SQLAlchemy ORM and SQLAlchemy Core expressions (`select()`, `where()`). Zero raw string concatenation. | **VERIFIED** |
| **CORS Origins** | Cross-Origin resource theft from unauthorized web pages. | `CORSMiddleware` configured with explicit origin whitelist (`http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:3000`). Wildcard `*` disallowed. | **VERIFIED** |
| **Sensitive Data Exposure** | Stack traces or internal system paths leaked in HTTP 500 error responses. | Custom exception handlers (`qtrace_exception_handler`, `unhandled_exception_handler`) catch internal errors and emit sanitized JSON envelopes without exposing disk paths. | **VERIFIED** |
| **Arbitrary File Download** | User crafts export ID to stream arbitrary system files. | Export download routes look up records strictly through database ID and verify file exists within `storage/reports` before streaming. | **VERIFIED** |

---

## 3. Cryptographic Evidence Integrity

1. **SHA-256 Ingestion Roots**: Original images are hashed on raw byte stream upon entry. Hashes are permanently recorded in the database and embedded into case logs.
2. **Derivative Separation**: Derivative crops and difference maps are stored in isolated directories (`storage/derivatives/`) with distinct derivative hashes, never overwriting source evidence.
3. **Immutable Report Snapshots**: Report generation freezes full case state into `dossier_exports.snapshot_json`. Re-exporting increments the version and creates a separate physical file.
4. **Independent Hash Verification**: Downloaded PDF and JSON exports emit `X-Report-SHA256` headers matching physical byte hashes on disk with 100% bitwise parity.

---

## 4. Hardcoded Secrets & Environment Configuration Audit

- **Hardcoded Absolute Paths**: Scanned all `.py`, `.ts`, `.tsx`, and `.json` source files for machine-specific path literals (`D:\`, `C:\Users`). **Result: 0 found.**
- **Secret Keys & Passwords**: Local SQLite database uses local file access without embedded cloud tokens or credentials. Configuration is loaded via Pydantic `BaseSettings` from `.env`.
- **Default Debug Mode**: Default is `DEBUG=False` in `.env.example` and `backend/app/core/config.py`.

