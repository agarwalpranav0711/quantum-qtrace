# Q-TRACE Security Architecture, Threat Model & Privacy Controls

**Platform:** Q-TRACE — Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform  
**Version:** 1.0.0  
**Security Posture:** Local-First, Zero-Cloud, Air-Gapped Capable Forensics Workstation  

---

## 1. Threat Model & Security Posture

Digital evidence processing workstations operate in hostile environments where untrusted binary images submitted by claimants or external parties could contain active exploits, malformed payloads, or metadata designed to compromise the forensic workstation.

### In-Scope Threat Vectors
1. **Malicious Image Payloads:** Polyglot files, embedded executable scripts within EXIF/XMP tags, or buffer overflow payloads exploiting image decoding libraries (`libjpeg`, `libpng`, `libtiff`).
2. **Decompression Bomb Denial-of-Service (DoS):** Pixel-flood ZIP bombs or compressed TIFF/PNG files with tiny disk footprints that expand to dozens of gigabytes in RAM upon decoding.
3. **Path Traversal & Arbitrary File Overwrite:** Exploits attempting to escape the evidence storage directory via `../` sequences or null byte injection (`%00`).
4. **Evidence Tampering & Chain-of-Custody Invalidation:** Modification or replacement of ingested master evidence files on disk after case initialization.
5. **PII & Privacy Leakage:** Unintended exposure or broadcast of sensitive Vehicle Identification Numbers (VIN), residential location coordinates (GPS), or vehicle license plates.

---

## 2. Evidence Integrity & Chain-of-Custody Architecture

### 2.1 Write-Once, Read-Many (WORM) Storage Policy
- **Cryptographic Sealing:** The exact byte stream of an ingested image is digested using SHA-256 prior to any metadata parsing, format transformation, or disk writes.
- **Master Isolation:** Master files are stored in `storage/originals/` keyed by immutable UUIDv4 strings. Raw original files are never altered, normalized, or overwritten.
- **On-Demand Verification:** The backend exposes a `/verify` endpoint that recomputes the SHA-256 digest directly from the disk block and compares it against the immutable database registry. Any discrepancy raises an immediate `EVIDENCE_TAMPERING_DETECTED` alert.

```
[Untrusted Client Upload]
          │
          ▼
[Magic-Byte Header Validation] ──(Invalid)──► Reject (400 Bad Request)
          │
          ▼
[SHA-256 Digest Calculation] ──► Record in SQLite Immutable Registry
          │
          ▼
[WORM Master Store] ──► storage/originals/{uuid}.ext
          │
          ▼
[Derivative Pipeline] ──► Generates cached analysis derivatives in storage/derivatives/
```

---

## 3. Input Validation & Hardening Controls

### 3.1 Magic-Byte File Type Verification
Q-TRACE validates uploaded files using physical byte signatures, ignoring client-provided MIME headers and extensions:
- **JPEG:** `FF D8 FF`
- **PNG:** `89 50 4E 47 0D 0A 1A 0A`
- **TIFF (Little Endian):** `49 49 2A 00`
- **TIFF (Big Endian):** `4D 4D 00 2A`
- **WebP:** `52 49 46 46` ... `57 45 42 50`

### 3.2 Decompression Bomb Mitigation
Image dimension bounds are enforced before rasterization. Image decoding is capped at $100,000,000\text{ pixels}$ ($100\text{ MP}$) and $50\text{ MB}$ raw upload size:
```python
Image.MAX_IMAGE_PIXELS = 100_000_000
```
Attempts to process images exceeding these dimensions raise `ImageBombError` and abort processing without allocating heap memory.

### 3.3 Path Traversal Defense
All storage paths are resolved using canonicalized path resolution:
```python
resolved_path = (STORAGE_BASE_DIR / filename).resolve()
if not resolved_path.is_relative_to(STORAGE_BASE_DIR.resolve()):
    raise SecurityException("Path traversal attempt detected.")
```
Null bytes and control characters are stripped prior to filesystem operations.

---

## 4. Privacy, PII Protection & Data Governance

1. **Zero External Network Exfiltration:**
   - Q-TRACE operates strictly locally on `localhost:8000` (backend) and `localhost:5173` (frontend).
   - No telemetry, analytics, cloud tracking, or remote API calls exist in the codebase.
   - The entire platform runs in fully air-gapped forensic environments.
2. **Metadata Redaction Options:**
   - When generating external dossiers, investigators can selectively redact high-precision GPS coordinates, owner names, and serial numbers.
3. **Local Database Security:**
   - SQLite databases are created with standard local file permissions and exclude network-accessible database ports.
