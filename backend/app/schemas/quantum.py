"""Schemas for quantum image comparison API requests and responses."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class QuantumComparisonRequest(BaseModel):
    """Request payload for comparing two 4x4 image patches via quantum circuit."""

    patch_a: List[List[int]] = Field(
        ...,
        description="4x4 pixel intensity matrix for Patch A (4-bit grayscale values: 0 to 15)",
    )
    patch_b: List[List[int]] = Field(
        ...,
        description="4x4 pixel intensity matrix for Patch B (4-bit grayscale values: 0 to 15)",
    )
    architecture: Literal["16q", "12q"] = Field(
        default="16q",
        description="Quantum comparison circuit architecture ('16q' NEQR baseline or '12q' resource-optimized)",
    )
    shots: Optional[int] = Field(
        default=None,
        description="Number of simulation measurement shots. If None, defaults to 1024.",
        ge=1,
        le=50000,
    )

    @field_validator("patch_a", "patch_b")
    @classmethod
    def validate_patch_dimensions_and_values(cls, v: List[List[int]]) -> List[List[int]]:
        """Ensure patches are strictly 4x4 with integer pixel values in [0, 255]."""
        if len(v) != 4:
            raise ValueError(f"Patch must have exactly 4 rows, got {len(v)}.")
        for row_idx, row in enumerate(v):
            if len(row) != 4:
                raise ValueError(
                    f"Patch row {row_idx} must have exactly 4 columns, got {len(row)}."
                )
            for col_idx, val in enumerate(row):
                if not (0 <= val <= 255):
                    raise ValueError(
                        f"Pixel at ({row_idx}, {col_idx}) must be in range [0, 255], got {val}."
                    )
        return v


class QuantumComparisonResponse(BaseModel):
    """Response containing quantum comparison results, circuit metrics, and diff maps."""

    architecture: str
    qubits: int
    depth: int
    gate_count: int
    fidelity: float
    reconstructed_diff_map: List[List[int]]
    classical_diff_map: List[List[int]]
    difference_count: int
    coverage_ratio: float
    shots_used: int
    execution_time_ms: float
    identical: bool
