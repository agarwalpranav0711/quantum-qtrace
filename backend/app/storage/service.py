"""Evidence storage service implementing WORM preservation and directory isolation."""

import os
import stat
from pathlib import Path
from typing import Tuple, Optional
from backend.app.core.config import get_settings
from backend.app.core.exceptions import StorageException, IntegrityException
from backend.app.core.logging import get_logger
from backend.app.storage.paths import (
    get_storage_root,
    get_subfolder_path,
    resolve_safe_path,
)

logger = get_logger("storage")

SUBFOLDERS = [
    "originals",
    "derivatives",
    "analysis",
    "experiments",
    "reports",
    "temp",
]


class StorageService:
    """Manages file storage across isolated directories with WORM guarantees on originals."""

    def __init__(self, root_path: Optional[Path] = None) -> None:
        self.root = (root_path or get_storage_root()).resolve()
        self.ensure_storage_dirs()

    def ensure_storage_dirs(self) -> None:
        """Create all required storage subdirectories if they do not exist."""
        self.root.mkdir(parents=True, exist_ok=True)
        for folder_name in SUBFOLDERS:
            subfolder = self.root / folder_name
            subfolder.mkdir(parents=True, exist_ok=True)

    def get_category_dir(self, category: str) -> Path:
        """Get validated directory for a storage category."""
        if category not in SUBFOLDERS:
            raise StorageException(f"Invalid storage category: '{category}'.")
        return (self.root / category).resolve()

    def store_original(
        self,
        file_bytes: bytes,
        sha256_hash: str,
        original_filename: str,
    ) -> Tuple[Path, str]:
        """
        Store an original evidence file under WORM (Write-Once-Read-Many) semantics.

        The file is named deterministically by its SHA-256 hash to enforce content addressability.
        After writing, read-only permissions are enforced on disk.
        """
        originals_dir = self.get_category_dir("originals")
        _, ext = os.path.splitext(original_filename)
        safe_ext = ext.lower() if ext else ".bin"
        stored_filename = f"{sha256_hash}{safe_ext}"
        target_path = resolve_safe_path(originals_dir, stored_filename)

        if target_path.exists():
            # WORM principle: file is already preserved. Verify existing size.
            existing_size = target_path.stat().st_size
            if existing_size != len(file_bytes):
                raise IntegrityException(
                    f"Integrity conflict: file with SHA-256 {sha256_hash} already exists with size {existing_size} bytes."
                )
            logger.info(f"Original evidence {stored_filename} already stored (WORM deduplication).")
            return target_path, stored_filename

        try:
            # Write file bytes
            target_path.write_bytes(file_bytes)

            # Apply read-only permissions (WORM enforcement)
            # Remove write permissions for user, group, and other
            current_mode = target_path.stat().st_mode
            read_only_mode = current_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            os.chmod(target_path, read_only_mode)

            logger.info(f"Stored original evidence at {target_path} with read-only permissions.")
            return target_path, stored_filename
        except Exception as e:
            if target_path.exists() and not (target_path.stat().st_mode & stat.S_IREAD):
                # Clean up partial write if failed
                try:
                    os.chmod(target_path, stat.S_IWRITE)
                    target_path.unlink()
                except Exception:
                    pass
            raise StorageException(f"Failed to store original evidence: {str(e)}")

    def store_file(
        self,
        category: str,
        filename: str,
        file_bytes: bytes,
    ) -> Path:
        """Store a derived file, artifact, or temporary file in the specified category."""
        if category == "originals":
            raise StorageException(
                "Direct store_file() call forbidden for 'originals'. Use store_original() for WORM enforcement."
            )

        cat_dir = self.get_category_dir(category)
        target_path = resolve_safe_path(cat_dir, filename)

        try:
            target_path.write_bytes(file_bytes)
            return target_path
        except Exception as e:
            raise StorageException(f"Failed to store file in {category}: {str(e)}")

    def retrieve_file(self, category: str, filename: str) -> Path:
        """Retrieve a stored file path, verifying its existence and path safety."""
        cat_dir = self.get_category_dir(category)
        target_path = resolve_safe_path(cat_dir, filename)

        if not target_path.exists():
            raise StorageException(f"File '{filename}' not found in category '{category}'.")

        return target_path

    def delete_temporary(self, filename: str) -> bool:
        """Delete a file from the temporary staging folder."""
        temp_dir = self.get_category_dir("temp")
        target_path = resolve_safe_path(temp_dir, filename)

        if target_path.exists():
            target_path.unlink()
            return True
        return False


_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Return singleton StorageService instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

