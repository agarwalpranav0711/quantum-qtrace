"""Unit tests for the SHA-256 cryptographic integrity service."""

import hashlib
import stat
import os
from pathlib import Path
from backend.app.services.integrity import (
    compute_sha256_bytes,
    compute_sha256_file,
    verify_file_integrity,
)


def test_compute_sha256_bytes_matches_hashlib():
    """Ensure in-memory byte hashing exactly matches standard hashlib SHA-256."""
    payload = b"Q-TRACE Forensic Integrity Verification Test Payload 2026"
    expected = hashlib.sha256(payload).hexdigest().lower()
    computed = compute_sha256_bytes(payload)
    assert computed == expected


def test_compute_sha256_file_matches_bytes(tmp_path: Path):
    """Ensure streaming file hash matches in-memory hash."""
    test_file = tmp_path / "test_file.bin"
    payload = b"\x00\x01\x02\x03\xFF" * 10000  # 50 KB
    test_file.write_bytes(payload)

    byte_hash = compute_sha256_bytes(payload)
    file_hash = compute_sha256_file(test_file)
    assert byte_hash == file_hash


def test_verify_file_integrity_intact_and_tampered(tmp_path: Path):
    """Ensure file integrity verification succeeds for pristine data and catches tampering."""
    test_file = tmp_path / "evidence.bin"
    original_data = b"Original pristine forensic evidence bitstream"
    test_file.write_bytes(original_data)

    original_hash = compute_sha256_bytes(original_data)

    # 1. Verification of pristine file
    is_intact, current_hash = verify_file_integrity(test_file, original_hash)
    assert is_intact is True
    assert current_hash == original_hash

    # 2. Tamper: alter one byte
    os.chmod(test_file, stat.S_IWRITE)
    test_file.write_bytes(b"Original pristine forensic evidence bitstreaM")

    # 3. Verification of tampered file
    is_intact_tampered, tampered_hash = verify_file_integrity(test_file, original_hash)
    assert is_intact_tampered is False
    assert tampered_hash != original_hash

