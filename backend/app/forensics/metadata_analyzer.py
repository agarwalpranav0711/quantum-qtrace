"""Metadata and EXIF forensic analyzer."""

import io
import time
import re
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ExifTags

from backend.app.forensics.base import ForensicTechnique
from backend.app.forensics.schemas import (
    TechniqueResult,
    ForensicStatus,
    FindingCategory,
    FindingItem,
    ArtifactReference,
)
from backend.app.storage.service import StorageService
from backend.app.services.integrity import compute_sha256_bytes

EDITING_SOFTWARE_KEYWORDS = [
    "photoshop", "gimp", "canva", "snapseed", "lightroom", "paint.net",
    "affinity", "corel", "pixlr", "vsco", "facetune", "inpaint",
]


class MetadataAnalyzer(ForensicTechnique):
    """Examines image container format, structural headers, and embedded EXIF metadata."""

    id: str = "metadata"
    name: str = "Image Metadata & EXIF Integrity"
    version: str = "1.0.0"
    category: str = "Container & Provenance"
    description: str = (
        "Parses structural container headers, embedded EXIF tags, camera hardware parameters, "
        "timestamps, and digital editing software signatures."
    )
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {}
    limitations: List[str] = [
        "Metadata can be trivially stripped, modified, or forged using standard command-line tools.",
        "Social media and messaging platforms (e.g. WhatsApp, iMessage) routinely strip EXIF during transmission.",
        "The complete absence of EXIF metadata must NEVER be treated as conclusive proof of fraud.",
    ]

    def analyze(
        self,
        image_path: Path,
        image_bytes: bytes,
        parameters: Dict[str, Any],
        storage_service: StorageService,
        analysis_id: str,
    ) -> TechniqueResult:
        start_time = time.perf_counter()
        observations: List[FindingItem] = []
        indicators: List[FindingItem] = []
        hypotheses: List[FindingItem] = []
        metrics: Dict[str, Any] = {}
        artifacts: List[ArtifactReference] = []
        warnings: List[str] = []

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img_format = img.format or "UNKNOWN"
                width, height = img.size
                mode = img.mode
                info_keys = list(img.info.keys())
                file_size_bytes = len(image_bytes)

                metrics["format"] = img_format
                metrics["dimensions"] = {"width": width, "height": height}
                metrics["color_mode"] = mode
                metrics["file_size_bytes"] = file_size_bytes

                observations.append(
                    FindingItem(
                        category=FindingCategory.OBSERVATION,
                        title="Container Properties",
                        description=f"Format: {img_format}, Dimensions: {width}x{height} px, Color Mode: {mode}, File Size: {file_size_bytes:,} bytes.",
                        details={"format": img_format, "width": width, "height": height, "mode": mode, "size": file_size_bytes},
                    )
                )

                # 1. Parse EXIF data if present
                exif_data: Dict[str, Any] = {}
                has_exif = False
                raw_exif = img.getexif()

                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        # Clean binary or undecodable values
                        if isinstance(value, bytes):
                            try:
                                exif_data[tag_name] = value.decode("utf-8", errors="replace").strip("\x00")
                            except Exception:
                                exif_data[tag_name] = f"<binary data: {len(value)} bytes>"
                        else:
                            exif_data[tag_name] = str(value)

                    if exif_data:
                        has_exif = True

                metrics["has_exif"] = has_exif
                metrics["exif_tag_count"] = len(exif_data)
                metrics["exif_tags"] = exif_data

                if has_exif:
                    # Camera details
                    make = exif_data.get("Make", "Unknown")
                    model = exif_data.get("Model", "Unknown")
                    observations.append(
                        FindingItem(
                            category=FindingCategory.OBSERVATION,
                            title="Camera Hardware Signature",
                            description=f"Device: {make} {model}.",
                            details={"make": make, "model": model},
                        )
                    )

                    # Timestamps
                    dt_orig = exif_data.get("DateTimeOriginal")
                    dt_digit = exif_data.get("DateTimeDigitized")
                    dt_mod = exif_data.get("DateTime")
                    observations.append(
                        FindingItem(
                            category=FindingCategory.OBSERVATION,
                            title="Embedded Timestamps",
                            description=f"Original: {dt_orig or 'N/A'}, Digitized: {dt_digit or 'N/A'}, Modified: {dt_mod or 'N/A'}.",
                            details={"original": dt_orig, "digitized": dt_digit, "modified": dt_mod},
                        )
                    )

                    # Check for editing software tags
                    software_tag = exif_data.get("Software", "")
                    processing_tag = exif_data.get("ProcessingSoftware", "")
                    combined_software = f"{software_tag} {processing_tag}".lower()

                    for kw in EDITING_SOFTWARE_KEYWORDS:
                        if kw in combined_software:
                            indicators.append(
                                FindingItem(
                                    category=FindingCategory.INDICATOR,
                                    title="Editing Software Signature Detected",
                                    description=(
                                        f"EXIF tag indicates processing by digital editing software: '{software_tag or processing_tag}'. "
                                        "This indicates post-capture manipulation or re-saving."
                                    ),
                                    confidence=0.85,
                                    details={"detected_keyword": kw, "software": software_tag, "processing": processing_tag},
                                )
                            )
                            hypotheses.append(
                                FindingItem(
                                    category=FindingCategory.HYPOTHESIS,
                                    title="Post-Capture Modification",
                                    description="Image was exported or re-saved using photo editing software rather than directly from camera hardware.",
                                    details={"software": software_tag},
                                )
                            )
                            break
                else:
                    observations.append(
                        FindingItem(
                            category=FindingCategory.OBSERVATION,
                            title="No Embedded EXIF Metadata",
                            description="Image container lacks EXIF metadata tags. Common in web-optimized images, messaging app transfers, or scrubbed evidence.",
                            details={},
                        )
                    )

                # 2. Check for Embedded Thumbnail Discrepancy
                has_thumbnail = False
                if hasattr(img, "_getexif"):
                    try:
                        exif_dict = img._getexif()
                        if exif_dict and 0x0201 in exif_dict and 0x0202 in exif_dict:
                            has_thumbnail = True
                    except Exception:
                        pass
                metrics["has_embedded_thumbnail"] = has_thumbnail

                # 3. Check for C2PA / JUMBF provenance containers
                has_c2pa = False
                c2pa_pattern = b"c2pa"
                jumbf_pattern = b"jumb"
                if c2pa_pattern in image_bytes or jumbf_pattern in image_bytes:
                    has_c2pa = True
                    observations.append(
                        FindingItem(
                            category=FindingCategory.OBSERVATION,
                            title="Content Credentials (C2PA) Signature",
                            description="Found JUMBF/C2PA provenance container markers in image byte stream.",
                            details={"has_c2pa": True},
                        )
                    )
                metrics["has_c2pa_manifest"] = has_c2pa

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return TechniqueResult(
                technique_id=self.id,
                technique_name=self.name,
                version=self.version,
                category=self.category,
                status=ForensicStatus.ANALYSIS_FAILED,
                execution_time_ms=elapsed,
                parameters_used=parameters,
                error_message=f"Metadata parsing failed: {str(e)}",
                limitations=self.limitations,
            )

        elapsed = (time.perf_counter() - start_time) * 1000.0
        status = ForensicStatus.POTENTIAL_INDICATOR_DETECTED if indicators else ForensicStatus.NO_ANOMALY_DETECTED

        return TechniqueResult(
            technique_id=self.id,
            technique_name=self.name,
            version=self.version,
            category=self.category,
            status=status,
            execution_time_ms=elapsed,
            parameters_used=parameters,
            observations=observations,
            indicators=indicators,
            hypotheses=hypotheses,
            metrics=metrics,
            artifacts=artifacts,
            limitations=self.limitations,
            warnings=warnings,
        )

