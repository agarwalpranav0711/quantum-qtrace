"""File safety, magic-byte inspection, and image validation service."""

import io
import re
from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import Image
from backend.app.core.config import get_settings
from backend.app.core.exceptions import ValidationException

# Mitigate decompression-bomb denial-of-service attacks
Image.MAX_IMAGE_PIXELS = 100_000_000

# Recognized image magic byte signatures
MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/tiff": [b"II*\x00", b"MM\x00*"],
}

EXTENSION_MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}


@dataclass
class ImageValidationResult:
    """Detailed result of file validation."""
    is_valid: bool
    mime_type: str
    width: int
    height: int
    file_size: int
    sanitized_filename: str


def sanitize_filename(filename: str) -> str:
    """Sanitize original filename to prevent path injection and invalid characters."""
    # Remove directory paths if present
    filename = filename.replace("\\", "/").split("/")[-1]
    # Remove null bytes and non-printable characters
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)
    # Replace unsafe characters with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    # Ensure reasonable length
    if len(sanitized) > 128:
        base, ext = sanitized[:120], sanitized[-8:]
        sanitized = base + ext
    return sanitized or "evidence_file.bin"


def detect_mime_from_magic_bytes(header: bytes) -> Optional[str]:
    """Inspect the first bytes of a file to detect its real MIME type."""
    for mime, signatures in MAGIC_SIGNATURES.items():
        for sig in signatures:
            if header.startswith(sig):
                return mime
    return None


def validate_image_file(file_bytes: bytes, filename: str) -> ImageValidationResult:
    """
    Perform rigorous multi-stage security validation on an uploaded image file:
    1. Size limit enforcement.
    2. Magic byte header inspection.
    3. Extension consistency verification.
    4. Decompression-bomb and dimension boundary checks via PIL.
    """
    settings = get_settings()

    # 1. Size Check
    file_size = len(file_bytes)
    if file_size == 0:
        raise ValidationException("Uploaded file is empty (0 bytes).")
    if file_size > settings.MAX_UPLOAD_BYTES:
        raise ValidationException(
            f"File size ({file_size} bytes) exceeds maximum permitted limit ({settings.MAX_UPLOAD_BYTES} bytes)."
        )

    # 2. Magic Byte Check
    detected_mime = detect_mime_from_magic_bytes(file_bytes[:16])
    if not detected_mime:
        raise ValidationException(
            "Unsupported file format or invalid magic bytes. Only JPEG, PNG, and TIFF images are accepted."
        )

    # 3. Filename & Extension Sanitization
    safe_name = sanitize_filename(filename)
    ext = "." + safe_name.split(".")[-1].lower() if "." in safe_name else ""
    expected_mime = EXTENSION_MIME_MAP.get(ext)

    if not expected_mime:
        raise ValidationException(
            f"File extension '{ext}' is not permitted. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
        )

    if detected_mime != expected_mime:
        raise ValidationException(
            f"MIME type mismatch: extension '{ext}' implies '{expected_mime}' but magic bytes indicate '{detected_mime}'."
        )

    # 4. Decompression Bomb and Dimension Bounds Check
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()

        # Re-open to read dimensions since verify() may close the stream
        with Image.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size

            if width > settings.MAX_IMAGE_WIDTH or height > settings.MAX_IMAGE_HEIGHT:
                raise ValidationException(
                    f"Image dimensions ({width}x{height}) exceed maximum allowed limits "
                    f"({settings.MAX_IMAGE_WIDTH}x{settings.MAX_IMAGE_HEIGHT})."
                )

            if width <= 0 or height <= 0:
                raise ValidationException(f"Invalid image dimensions: {width}x{height}.")

    except ValidationException:
        raise
    except Image.DecompressionBombError as e:
        raise ValidationException(f"Image rejected: potential decompression bomb detected ({str(e)}).")
    except Exception as e:
        raise ValidationException(f"Failed to decode or parse image structure: {str(e)}")

    return ImageValidationResult(
        is_valid=True,
        mime_type=detected_mime,
        width=width,
        height=height,
        file_size=file_size,
        sanitized_filename=safe_name,
    )

