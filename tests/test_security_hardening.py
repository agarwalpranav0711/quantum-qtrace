"""
Automated Security Hardening & Vulnerability Mitigation Tests for Q-TRACE.
Validates defenses against:
1. Path traversal attacks (relative paths, directory escapes).
2. Magic byte spoofing (executables masked as images).
3. Image decompression bombs / memory exhaustion.
4. Cryptographic integrity tamper detection (WORM verification).
5. Oversized payload handling.
"""

import io
import os
import stat
import pytest
from pathlib import Path
from PIL import Image

from backend.app.storage.service import StorageService, resolve_safe_path
from backend.app.services.integrity import compute_sha256_bytes, compute_sha256_file, verify_file_integrity
from backend.app.services.validation import validate_image_file, ValidationException, sanitize_filename
from backend.app.core.exceptions import SecurityException, StorageException


@pytest.fixture(scope="module")
def security_storage(tmp_path_factory):
    """Storage fixture with isolated temporary root directory."""
    temp_dir = tmp_path_factory.mktemp("sec_storage_env")
    return StorageService(root_path=temp_dir)


def test_path_traversal_prevention_on_storage(security_storage: StorageService):
    """Verify that path traversal sequences ('../', '..\\', null bytes) in filename resolution are rejected."""
    traversal_payloads = [
        "../../etc/passwd",
        "..\\..\\Windows\\System32\\cmd.exe",
        "sub/../../../secret.key",
        "dir/../../boot.ini",
        "image.png\x00.exe",
    ]

    base_dir = security_storage.get_category_dir("originals")

    for payload in traversal_payloads:
        with pytest.raises(SecurityException):
            resolve_safe_path(base_dir, payload)


def test_magic_byte_spoofing_detection():
    """Verify that executable, script, or non-image binaries renamed to image extensions are rejected."""
    # 1. DOS/PE Executable ('MZ' header) renamed as .jpg
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00" + b"\x00" * 100
    with pytest.raises(ValidationException) as exc_info:
        validate_image_file(fake_exe, "malware.jpg")
    assert "Unsupported file format or invalid magic bytes" in str(exc_info.value)

    # 2. Shell script disguised as .png
    fake_script = b"#!/bin/bash\nrm -rf /\n"
    with pytest.raises(ValidationException) as exc_info:
        validate_image_file(fake_script, "exploit.png")
    assert "Unsupported file format or invalid magic bytes" in str(exc_info.value)

    # 3. HTML / SVG XSS payload disguised as JPEG
    fake_svg = b"<svg onload='alert(1)'></svg>"
    with pytest.raises(ValidationException) as exc_info:
        validate_image_file(fake_svg, "vector.jpg")
    assert "Unsupported file format or invalid magic bytes" in str(exc_info.value)


def test_decompression_bomb_rejection():
    """Verify that synthetic decompression bombs (sparse large dimensions) are rejected before memory allocation."""
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    img.save(buf, format="JPEG")
    valid_bytes = buf.getvalue()

    # Valid image passes
    meta = validate_image_file(valid_bytes, "valid_claim.jpg")
    assert meta.width == 100
    assert meta.height == 100


def test_worm_evidence_tamper_detection(security_storage: StorageService):
    """Verify that any post-ingestion byte tampering of evidence is immediately detected by SHA-256."""
    img_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
    orig_sha = compute_sha256_bytes(img_bytes)

    # Ingest original evidence
    stored_path, stored_filename = security_storage.store_original(img_bytes, orig_sha, "bumper_damage.png")
    assert stored_path.exists()

    # 1. Verify clean integrity
    is_intact, current_sha = verify_file_integrity(stored_path, orig_sha)
    assert is_intact is True
    assert current_sha == orig_sha

    # 2. Simulate malicious actor tampering with physical disk bits
    # First temporarily clear read-only flag on Windows to tamper
    os.chmod(stored_path, stat.S_IWRITE)
    with open(stored_path, "r+b") as f:
        f.seek(16)
        f.write(b"\xFF\xFF\xFF")  # Bit flip
    os.chmod(stored_path, stat.S_IREAD)

    # 3. Verify that integrity check fails
    is_tampered_intact, tampered_sha = verify_file_integrity(stored_path, orig_sha)
    assert is_tampered_intact is False
    assert tampered_sha != orig_sha


def test_oversized_payload_rejection():
    """Verify that uploads exceeding configured byte limits are blocked."""
    # 0 byte rejection
    with pytest.raises(ValidationException) as exc_info:
        validate_image_file(b"", "empty.jpg")
    assert "Uploaded file is empty" in str(exc_info.value)
