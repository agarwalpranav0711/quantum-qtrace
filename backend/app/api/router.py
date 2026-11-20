"""Main API router combining all subsystem endpoints under /api/v1."""

from fastapi import APIRouter
from backend.app.api.health import router as health_router
from backend.app.api.cases import router as cases_router
from backend.app.api.quantum import router as quantum_router
from backend.app.api.forensics import router as forensics_router
from backend.app.api.canvas import router as canvas_router
from backend.app.api.dossier import router as dossier_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount subsystem routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(cases_router)
api_v1_router.include_router(quantum_router)
api_v1_router.include_router(forensics_router)
api_v1_router.include_router(canvas_router)
api_v1_router.include_router(dossier_router)

