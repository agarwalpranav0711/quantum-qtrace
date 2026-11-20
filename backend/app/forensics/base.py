"""Abstract base class for all classical image forensic techniques."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Tuple, List
from backend.app.storage.service import StorageService
from backend.app.forensics.schemas import TechniqueResult, TechniqueDescriptor


class ForensicTechnique(ABC):
    """Abstract interface implemented by all forensic analysis modules."""

    id: str = "base"
    name: str = "Base Technique"
    version: str = "1.0.0"
    category: str = "General"
    description: str = ""
    supported_formats: List[str] = ["image/jpeg", "image/png", "image/tiff"]
    default_parameters: Dict[str, Any] = {}
    limitations: List[str] = []

    def get_descriptor(self) -> TechniqueDescriptor:
        """Return public metadata descriptor for this technique."""
        return TechniqueDescriptor(
            id=self.id,
            name=self.name,
            version=self.version,
            category=self.category,
            description=self.description,
            supported_formats=self.supported_formats,
            default_parameters=self.default_parameters,
            limitations=self.limitations,
        )

    def is_applicable(self, mime_type: str, image_bytes: bytes) -> Tuple[bool, str]:
        """
        Check whether this technique is technically applicable to the provided image.
        Returns (is_applicable, reason_if_not).
        """
        if self.supported_formats and mime_type.lower() not in [fmt.lower() for fmt in self.supported_formats]:
            return False, f"Format '{mime_type}' not supported by {self.name} (requires {', '.join(self.supported_formats)})."
        return True, ""

    @abstractmethod
    def analyze(
        self,
        image_path: Path,
        image_bytes: bytes,
        parameters: Dict[str, Any],
        storage_service: StorageService,
        analysis_id: str,
    ) -> TechniqueResult:
        """
        Execute forensic analysis on the provided image bytes.

        Guarantees:
        - NEVER modifies the original image file or bytes.
        - Generates artifacts strictly through storage_service under category 'analysis'.
        - Returns a structured TechniqueResult with observations, indicators, metrics, and limitations.
        """
        pass

