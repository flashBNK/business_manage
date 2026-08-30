from fastapi import APIRouter

from .structure.routers import router as structure_router

router = APIRouter(prefix="/api/v1")
router.include_router(structure_router)
