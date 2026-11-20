# Q-TRACE: Privacy & Sensitive Data Handling Protocol

**Document Reference:** `docs/PRIVACY_AND_DATA_HANDLING.md`  
**Classification:** Data Privacy & Regulatory Compliance (GDPR, CCPA)  
**Version:** 1.9.0  

---

## 1. Sensitive Data Domains in Vehicular Forensics

Photographs submitted in motor-vehicle insurance claims frequently capture sensitive Personally Identifiable Information (PII) and contextual data:
1. **Vehicle Identification Numbers (VIN):** Stamped on door jambs, dashboards, and engine firewalls.
2. **License Plate Numbers:** Direct identifiers linking images to registered vehicle owners.
3. **Claimant Likeness & Bystanders:** Faces reflected in vehicle windows or standing adjacent to accident scenes.
4. **Precise Geographic EXIF GPS Coordinates:** Exact latitude, longitude, and elevation of home driveways or collision locations.

---

## 2. Q-TRACE Privacy Protections

### 2.1 Complete Local-First Data Isolation
- **Zero Cloud Leakage:** Unlike SaaS forensic tools that upload evidence to third-party cloud servers for processing, Q-TRACE runs entirely on the investigator's local workstation.
- **No Remote Telemetry:** No analytics pings, crash reports, or telemetry bytes leave the system.

### 2.2 EXIF Location Disclosure & Privacy Shielding
- When extracting EXIF metadata, the `MetadataAnalyzer` partitions GPS coordinates into a distinct structured dictionary.
- The reporting engine flags GPS coordinates with a privacy banner: *"Contains precise geolocation coordinates; sanitize prior to public disclosure."*
- Examiners can configure dossier export profiles to redact raw GPS coordinates while preserving camera make, model, and software tags.

### 2.3 Local Storage Lifecycle & Right to Erasure
- Cases, evidence items, and generated derivative artifacts are stored in predictable local directories (`storage/`).
- The `scripts/reset_demo_data.py` utility completely purges all local database records and physical image files upon case conclusion, satisfying corporate data retention schedules and GDPR Article 17 ("Right to Erasure").

