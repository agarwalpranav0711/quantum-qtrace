# Q-TRACE: Threat Model & Security Boundary Specification

**Document Reference:** `docs/THREAT_MODEL.md`  
**Classification:** Threat Modeling & Risk Governance (STRIDE Framework)  
**Version:** 1.9.0  

---

## 1. Threat Modeling Overview (STRIDE Analysis)

Q-TRACE applies the industry-standard STRIDE threat categorization framework to the digital forensics workstation domain:

| STRIDE Category | Potential Threat Vector in Forensics | Q-TRACE Architectural Mitigation | Residual Risk |
| :--- | :--- | :--- | :--- |
| **Spoofing Identity** | Unauthorized user attempting to pose as the lead forensic examiner. | Single-user local-first architecture; audit logs bind events to the local operating system account and explicit author names in database records. | Workstation physical access security (mitigated by OS lock screen). |
| **Tampering with Data** | A claimant or corrupt party editing stored evidence photos on disk to alter forensic outputs. | Content-addressed storage, NTFS read-only file attributes, automated SHA-256 integrity verification before every analysis pass. | Negligible; any byte change fails hash check and halts analysis. |
| **Repudiation** | An examiner claiming they never modified an ROI or ran a specific analysis. | Append-only event history ledger in SQLite WAL; versioned dossier export snapshots frozen with immutable timestamps. | Minimal; records are cryptographically dated. |
| **Information Disclosure** | Leakage of confidential accident photographs, claimant PII, or vehicle license plates to external cloud servers. | Local-first design: zero outbound cloud network calls; all models, circuits, and algorithms execute entirely on the local host CPU. | Zero external cloud exposure. |
| **Denial of Service** | Decompression bombs or corrupt image payloads crashing the examiner's workstation. | Strict file header verification, `MAX_IMAGE_PIXELS` memory bounds, input size ceilings, and isolated exception handlers. | Low; malformed files are caught and isolated. |
| **Elevation of Privilege** | Path traversal or script injection via crafted EXIF metadata or malicious filenames. | Strict regex filename sanitization, `resolve_safe_path` directory containment, and parameter binding in database queries. | Low; verified by automated security test suite. |

---

## 2. Security Boundaries & Assumptions

1. **Host Boundary:** Q-TRACE assumes the host Windows operating system is secure and not compromised by root-level kernel keyloggers or ransomware.
2. **Local Isolation:** The local HTTP API binds strictly to `127.0.0.1` (localhost). It must not be exposed to the public internet without an authenticating reverse proxy (e.g. Nginx with TLS and mTLS).
3. **Evidence Storage Boundary:** Storage directories (`storage/originals/`) must remain on a dedicated NTFS filesystem with proper user access control lists (ACLs).

