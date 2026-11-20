"""API routes for quantum image comparison and circuit analysis."""

from fastapi import APIRouter, Depends, status
from backend.app.schemas.quantum import (
    QuantumComparisonRequest,
    QuantumComparisonResponse,
)
from backend.app.integrations.quantum_adapter import (
    QuantumAdapter,
    get_quantum_adapter,
)

router = APIRouter(prefix="/quantum", tags=["Quantum Image Comparison"])


@router.post(
    "/compare",
    response_model=QuantumComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare two 4x4 image patches using a quantum circuit",
)
def compare_quantum_patches(
    payload: QuantumComparisonRequest,
    adapter: QuantumAdapter = Depends(get_quantum_adapter),
) -> QuantumComparisonResponse:
    """
    Execute quantum image comparison on two 4x4 pixel matrices.

    - **patch_a**: 4x4 array of pixel intensities (0-255).
    - **patch_b**: 4x4 array of pixel intensities (0-255).
    - **architecture**: '16q' (NEQR dual-register baseline) or '12q' (resource-optimized single-register).
    - **shots**: Optional number of measurement shots (defaults to coupon collector optimal sampling).
    """
    result = adapter.run_comparison(
        patch_a=payload.patch_a,
        patch_b=payload.patch_b,
        architecture=payload.architecture,
        shots=payload.shots,
    )
    return QuantumComparisonResponse(**result)

