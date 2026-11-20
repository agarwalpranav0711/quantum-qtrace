# Q-TRACE Evidence Storage Architecture & WORM Policy

## 1. Evidence Storage Principles

In forensic image intelligence, evidence admissibility hinges upon provable bitstream preservation. An evidence handling system must guarantee that:
1. An evidence file is never modified in-place after initial receipt.
2. An investigator or algorithmic task always operates on isolated working derivatives, never the master bitstream.
3. Path manipulation or directory traversal exploits cannot compromise the host system.

To satisfy these requirements, Q-TRACE implements an isolated local filesystem hierarchy governed by **Write-Once-Read-Many (WORM)** rules.

---

## 2. Directory Hierarchy and Access Isolation

The physical storage root (`storage/`, configurable via `STORAGE_ROOT` in `.env`) is partitioned into six purpose-specific subfolders:

```text
storage/
├── originals/      # Master evidence files (WORM, read-only permissions locked)
├── derivatives/    # Working derivatives (normalized 8-bit PNGs, patch crops, thumbnails)
├── analysis/       # Algorithmic outputs (generated difference maps, feature plots)
├── experiments/    # Benchmark datasets and simulation logs
├── reports/        # Exported forensic intelligence dossiers (PDF / JSON)
└── temp/           # Transient upload buffer (scrubbed automatically)
```

| Category Directory | Permitted Operations | Immutability Policy | File Retention |
| :--- | :--- | :--- | :--- |
| `storage/originals/` | Write-Once (at ingestion), Read-Many | **Strict WORM**: Read-only OS permissions applied immediately; in-place edits and overwrites strictly prohibited. | Indefinite (Case lifecycle) |
| `storage/derivatives/` | Create, Read, Delete | Mutable: Working representations generated from originals for image processing. | Re-creatable from original |
| `storage/analysis/` | Create, Read, Delete | Append-only per analysis run: Stores difference maps and metrics. | Retained with Analysis record |
| `storage/experiments/` | Create, Read, Update | Experimental: Simulation matrices and empirical logs. | Project lifecycle |
| `storage/reports/` | Create, Read, Delete | Finalized: Exported investigation reports. | Case closure |
| `storage/temp/` | Create, Read, Delete | Ephemeral: Ingestion staging. Cleaned up upon completion. | Ephemeral |

---

## 3. WORM Preservation Implementation

### 3.1 Content-Addressed Naming
When an evidence image is submitted, Q-TRACE computes its 256-bit cryptographic digest. The stored filename is generated deterministically from its hexadecimal SHA-256 string:

$$\text{stored\_filename} = \text{SHA256}(\text{file\_bytes}) + \text{sanitized\_extension}$$

Example:
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.png`

### 3.2 Permission Locking
Upon completing the initial byte write to `storage/originals/`, the service strips write permissions at the operating system level (`backend/app/storage/service.py`):

```python
current_mode = target_path.stat().st_mode
read_only_mode = current_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
os.chmod(target_path, read_only_mode)
```

On Windows and POSIX systems, this sets the read-only file attribute, preventing accidental programmatic overwrites or modification by external tools.

### 3.3 Deduplication & Conflict Detection
If an identical file is ingested again (same SHA-256 hash):
- The service verifies that the existing on-disk file size matches the incoming payload.
- It reuses the preserved path rather than creating a duplicate, maintaining WORM integrity and saving disk space.
- If a hash collision occurs with mismatched byte lengths, the service raises a fatal `IntegrityException`.

---

## 4. Path Traversal & Injection Defense

To prevent path traversal attacks (such as `../../Windows/System32` or `..\..\..\etc\passwd`), every filesystem access is validated through `resolve_safe_path()` (`backend/app/storage/paths.py`):

1. **Null-Byte Injection Neutralization**: Checks for `\0` in the requested path, raising `SecurityException`.
2. **Path Normalization**: Resolves symbolic links and relative path segments (`..`, `.`) into an absolute target path.
3. **Strict Directory Confinement**:
   ```python
   try:
       candidate_path.relative_to(base_dir.resolve())
   except ValueError:
       raise SecurityException("Access denied: path traversal attempt detected.")
   ```
   If the resolved path does not reside strictly within the intended category subfolder, execution is terminated immediately with a 403 Forbidden response.

