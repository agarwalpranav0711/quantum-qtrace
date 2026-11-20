"""Technique registry managing discovery and cataloging of forensic modules."""

from typing import Dict, List, Optional
from backend.app.forensics.base import ForensicTechnique
from backend.app.forensics.schemas import TechniqueDescriptor
from backend.app.forensics.metadata_analyzer import MetadataAnalyzer
from backend.app.forensics.ela_analyzer import ErrorLevelAnalyzer
from backend.app.forensics.noise_analyzer import NoiseAnalyzer
from backend.app.forensics.copy_move_analyzer import CopyMoveAnalyzer
from backend.app.forensics.statistics_analyzer import StatisticsAnalyzer
from backend.app.forensics.perceptual_hash_analyzer import PerceptualHashAnalyzer
from backend.app.forensics.resampling_analyzer import ResamplingAnalyzer


class ForensicRegistry:
    """Central registry of classical forensic analysis techniques."""

    def __init__(self) -> None:
        self._techniques: Dict[str, ForensicTechnique] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register core classical forensic modules."""
        self.register(MetadataAnalyzer())
        self.register(ErrorLevelAnalyzer())
        self.register(NoiseAnalyzer())
        self.register(CopyMoveAnalyzer())
        self.register(StatisticsAnalyzer())
        self.register(PerceptualHashAnalyzer())
        self.register(ResamplingAnalyzer())

    def register(self, technique: ForensicTechnique) -> None:
        """Register a new technique instance."""
        self._techniques[technique.id] = technique

    def get(self, technique_id: str) -> Optional[ForensicTechnique]:
        """Fetch a technique by its ID."""
        return self._techniques.get(technique_id)

    def list_techniques(self) -> List[TechniqueDescriptor]:
        """List descriptors of all registered techniques."""
        return [t.get_descriptor() for t in self._techniques.values()]

    def list_technique_ids(self) -> List[str]:
        """List all registered technique IDs."""
        return list(self._techniques.keys())


_registry: Optional[ForensicRegistry] = None


def get_forensic_registry() -> ForensicRegistry:
    """Return singleton instance of ForensicRegistry."""
    global _registry
    if _registry is None:
        _registry = ForensicRegistry()
    return _registry

