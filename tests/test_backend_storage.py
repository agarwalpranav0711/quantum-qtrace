"""Unit tests for the evidence storage service and path security."""

import os
import stat
import pytest
from pathlib import Path
from backend.app.storage.service import StorageService
from backend.app.storage.paths import resolve_safe_path
from backend.app.core.exceptions import StorageException, SecurityException, IntegrityException


@pytest.fixture
def temp_storage(tmp_path: Path) -> StorageService:
    """Fixture providing an isolated StorageService in a temporary directory."""
    return StorageService(root_path=tmp_path)


def test_storage_subfolder_creation(temp_storage: StorageService):
    """Ensure all required isolated subfolders are created."""
    for folder in ["originals", "derivatives", "analysis", "experiments", "reports", "temp"]:
        sub = temp_storage.root / folder
        assert sub.exists()
        assert sub.is_dir()


def test_store_original_worm_semantics(temp_storage: StorageService):
    """Ensure original evidence is stored with WORM semantics and read-only attributes."""
    sample_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"A" * 50
    sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    path, stored_name = temp_storage.store_original(
        file_bytes=sample_bytes,
        sha256_hash=sha256,
        original_filename="sample.png",
    )

    assert path.exists()
    assert stored_name == f"{sha256}.png"
    assert path.read_bytes() == sample_bytes

    # Verify read-only permissions are enforced (on Windows, S_IREAD / not S_IWRITE)
    file_mode = path.stat().st_mode
    assert not (file_mode & stat.S_IWUSR), "File should be read-only under WORM policy"

    # Verify idempotency / deduplication: storing the same evidence again returns the existing path safely
    path2, stored_name2 = temp_storage.store_original(
        file_bytes=sample_bytes,
        sha256_hash=sha256,
        original_filename="sample.png",
    )
    assert path2 == path
    assert stored_name2 == stored_name


def test_store_original_integrity_conflict(temp_storage: StorageService):
    """Ensure storing different bytes with the same hash raises IntegrityException."""
    sample_bytes = b"InitialContent"
    sha256 = "test_hash_123"

    temp_storage.store_original(sample_bytes, sha256, "file.png")

    different_bytes = b"DifferentContentLongerBytes"
    with pytest.raises(IntegrityException):
        temp_storage.store_original(different_bytes, sha256, "file.png")


def test_path_traversal_prevention(temp_storage: StorageService):
    """Ensure directory traversal attacks are blocked by resolve_safe_path."""
    base_dir = temp_storage.get_category_dir("originals")

    # Relative traversal attempts
    with pytest.raises(SecurityException):
        resolve_safe_path(base_dir, "../../../evil.exe")

    with pytest.raises(SecurityException):
        resolve_safe_path(base_dir, "..\\..\\evil.exe")

    # Null byte attack
    with pytest.raises(SecurityException):
        resolve_safe_path(base_dir, "good.png\0.exe")


def test_forbidden_store_file_on_originals(temp_storage: StorageService):
    """Ensure generic store_file cannot bypass WORM store_original on 'originals' category."""
    with pytest.raises(StorageException):
        temp_storage.store_file("originals", "bypass.bin", b"data")


def test_temporary_file_lifecycle(temp_storage: StorageService):
    """Ensure temp files can be stored and deleted."""
    data = b"transient_data"
    temp_path = temp_storage.store_file("temp", "temp_01.tmp", data)
    assert temp_path.exists()

    deleted = temp_storage.delete_temporary("temp_01.tmp")
    assert deleted is True
    assert not temp_path.exists()

