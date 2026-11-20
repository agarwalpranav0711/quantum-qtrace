"""Unit tests for image file validation, format inspection, and security guards."""

import io
import pytest
from PIL import Image
from backend.app.services.validation import (
    validate_image_file,
    detect_mime_from_magic_bytes,
    sanitize_filename,
)
from backend.app.core.exceptions import ValidationException


def create_test_image(format: str, size: tuple = (64, 64), color: tuple = (100, 150, 200)) -> bytes:
    """Helper to generate valid encoded image bytes in memory."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_sanitize_filename():
    """Ensure filename sanitization strips malicious patterns and characters."""
    assert sanitize_filename("../../etc/passwd.png") == "passwd.png"
    assert sanitize_filename("..\\..\\windows\\system32.jpg") == "system32.jpg"
    assert sanitize_filename("bad\0file.png") == "badfile.png"
    assert sanitize_filename("safe_image_01.JPEG") == "safe_image_01.JPEG"


def test_detect_mime_magic_bytes():
    """Ensure magic byte detection works for valid JPEG and PNG headers."""
    png_bytes = create_test_image("PNG")
    jpeg_bytes = create_test_image("JPEG")
    fake_bytes = b"Just a plain text file pretending to be image"

    assert detect_mime_from_magic_bytes(png_bytes) == "image/png"
    assert detect_mime_from_magic_bytes(jpeg_bytes) == "image/jpeg"
    assert detect_mime_from_magic_bytes(fake_bytes) is None


def test_validate_valid_images():
    """Ensure valid PNG and JPEG files pass all validation checks."""
    png_bytes = create_test_image("PNG", size=(128, 128))
    res_png = validate_image_file(png_bytes, "photo.png")
    assert res_png.is_valid is True
    assert res_png.mime_type == "image/png"
    assert res_png.width == 128
    assert res_png.height == 128

    jpeg_bytes = create_test_image("JPEG", size=(64, 48))
    res_jpg = validate_image_file(jpeg_bytes, "claim_car.jpg")
    assert res_jpg.is_valid is True
    assert res_jpg.mime_type == "image/jpeg"
    assert res_jpg.width == 64
    assert res_jpg.height == 48


def test_reject_empty_file():
    """Ensure zero-byte uploads are rejected."""
    with pytest.raises(ValidationException, match="empty"):
        validate_image_file(b"", "empty.png")


def test_reject_mismatched_extension():
    """Ensure file with PNG bytes but .jpg extension is rejected."""
    png_bytes = create_test_image("PNG")
    with pytest.raises(ValidationException, match="MIME type mismatch"):
        validate_image_file(png_bytes, "fake_photo.jpg")


def test_reject_invalid_magic_bytes():
    """Ensure non-image files with valid extensions are rejected."""
    fake_png = b"Not really a PNG"
    with pytest.raises(ValidationException, match="Unsupported file format"):
        validate_image_file(fake_png, "fake.png")


def test_reject_excessive_dimensions():
    """Ensure images exceeding MAX_IMAGE_WIDTH/HEIGHT are rejected."""
    # Settings default is 8192
    with pytest.raises(ValidationException, match="exceed maximum allowed limits"):
        from backend.app.core.config import get_settings
        settings = get_settings()
        # Mocking or testing boundary by creating an oversized header
        oversized = create_test_image("PNG", size=(settings.MAX_IMAGE_WIDTH + 10, 10))
        validate_image_file(oversized, "huge.png")

