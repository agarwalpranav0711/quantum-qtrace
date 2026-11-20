# Q-TRACE: Security Hardening & Vulnerability Mitigation Architecture

**Document Reference:** `docs/PART9_SECURITY_HARDENING.md`  
**Classification:** Security Architecture & Penetration Defense  
**Version:** 1.9.0  

---

## 1. Security Architecture Overview

Because Q-TRACE is designed to operate on sensitive forensic evidence in high-stakes insurance claims, the application enforces defensive layers at every boundary:

```
+-------------------------------------------------------------------------------+
|                        Q-TRACE SECURITY DEFENSE LAYERS                        |
+-------------------------------------------------------------------------------+
| Layer 1: Ingestion & Boundary Sanitation                                      |
|   - Filename sanitization (replaces non-alphanumeric chars; strips null bytes)|
|   - Extension whitelist (.jpg, .jpeg, .png, .tif, .tiff)                     |
|   - Magic byte header inspection (detects disguised executables / PE / ELF)   |
|   - Maximum upload payload size ceiling (50 MB default)                       |
+-------------------------------------------------------------------------------+
| Layer 2: Decompression Bomb & Memory Shielding                               |
|   - Image.MAX_IMAGE_PIXELS ceiling (100,000,000 pixels)                      |
|   - Immediate dimension boundary check (rejects width/height > 10,000 px)     |
|   - Streaming chunk-based hashing (never loads 50 MB into RAM at once)        |
+-------------------------------------------------------------------------------+
| Layer 3: Storage Isolation & Path Traversal Prevention                        |
|   - resolve_safe_path() enforces canonical path containment                   |
|   - Relative sequences ('../', '..\\', null bytes) trigger SecurityException  |
|   - WORM file permissions (stat.S_IREAD read-only bit enforcement)            |
+-------------------------------------------------------------------------------+
| Layer 4: Cryptographic Tamper Detection & Audit Ledgers                       |
|   - Hardware SHA-256 calculation upon upload                                  |
|   - Real-time bitstream recalculation before running any analysis             |
|   - Immutable append-only audit event logging in SQLite                       |
+-------------------------------------------------------------------------------+
```

---

## 2. Verified Vulnerability Mitigations

| Vulnerability Vector | Attack Description | Q-TRACE Mitigation | Automated Test Coverage |
| :--- | :--- | :--- | :--- |
| **Path Traversal (CWE-22)** | Malicious filenames containing `../../Windows/System32/cmd.exe` attempting to read or overwrite host system files. | `resolve_safe_path` verifies `candidate.relative_to(base_dir)`. Rejects null bytes and traversal sequences. | `test_path_traversal_prevention_on_storage` |
| **Magic Byte Spoofing (CWE-434)** | Uploading an executable `.exe` or shell script `.sh` renamed with a `.jpg` extension to trigger code execution. | `validate_image_file` inspects the initial 16 physical bytes for known binary magic numbers (`\xFF\xD8\xFF`, `\x89PNG`). | `test_magic_byte_spoofing_detection` |
| **Decompression Bomb (CWE-400)** | Uploading a tiny compressed image that decompresses into billions of pixels, exhausting workstation RAM. | Sets `Image.MAX_IMAGE_PIXELS = 100,000,000`. Catches `DecompressionBombError` and aborts before full allocation. | `test_decompression_bomb_rejection` |
| **Physical Tampering (CWE-353)** | An adversary modifying physical evidence bytes directly on the workstation disk. | Any bit flip alters the SHA-256 digest. `verify_file_integrity` detects discrepancy and locks evidence item. | `test_worm_evidence_tamper_detection` |
| **Oversized Payloads (CWE-770)** | Submitting gigabyte-sized files to overwhelm server disk space. | Rejects files exceeding configured `MAX_UPLOAD_BYTES` (50MB) before buffering. | `test_oversized_payload_rejection` |

