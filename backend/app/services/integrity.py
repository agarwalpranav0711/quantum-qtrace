"""Cryptographic hashing and evidence integrity verification services."""

import hashlib
from pathlib import Path
from typing import Tuple, Union


def compute_sha256_bytes(data: bytes) -> str:
    """Compute standard hexadecimal SHA-256 digest of in-memory bytes."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest().lower()


def compute_sha256_file(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """Compute standard hexadecimal SHA-256 digest of a file on disk using streaming chunks."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hash calculation: {path}")

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest().lower()


def verify_file_integrity(
    file_path: Union[str, Path], expected_sha256: str
) -> Tuple[bool, str]:
    """
    Verify whether the on-disk file matches its expected SHA-256 hash.

    Returns:
        (is_intact, current_sha256_hash)
    """
    current_hash = compute_sha256_file(file_path)
    is_intact = current_hash.lower() == expected_sha256.lower()
    return is_intact, current_hash

