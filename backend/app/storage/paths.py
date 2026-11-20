"""Storage path resolution and directory traversal defense."""

import os
from pathlib import Path
from backend.app.core.config import get_settings
from backend.app.core.exceptions import SecurityException


def get_storage_root() -> Path:
    """Return the absolute path to the storage root."""
    settings = get_settings()
    return settings.storage_path


def get_subfolder_path(subfolder: str) -> Path:
    """Get absolute path to a specific storage subfolder."""
    root = get_storage_root()
    folder = (root / subfolder).resolve()
    return folder


def resolve_safe_path(base_dir: Path, filename: str) -> Path:
    """
    Resolve a filename within base_dir, strictly preventing directory traversal.

    Raises:
        SecurityException: If path traversal or null byte injection is detected.
    """
    if "\0" in filename:
        raise SecurityException("Null byte detected in file path.")

    # Remove any leading directory separators or relative segments
    clean_name = os.path.basename(filename)
    if clean_name != filename and not (filename.startswith("/") or filename.startswith("\\")):
        # In case a path with forward/backward slashes was passed
        parts = Path(filename).parts
        if any(p in ("..", ".", "") for p in parts):
            raise SecurityException(f"Path traversal attempt detected in: {filename}")

    candidate_path = (base_dir / clean_name).resolve()

    # Verify that the candidate path is strictly within the intended base directory
    try:
        candidate_path.relative_to(base_dir.resolve())
    except ValueError:
        raise SecurityException(
            f"Access denied: resolved path '{candidate_path}' is outside base directory '{base_dir}'."
        )

    return candidate_path

