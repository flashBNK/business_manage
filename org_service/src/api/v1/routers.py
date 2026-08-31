from fastapi import APIRouter

from .position.routers import router as position_router
from .struct_adm_position.routers import router as struct_adm_position_router
from .structure.routers import router as structure_router

router = APIRouter(prefix="/api/v1")
router.include_router(structure_router)
router.include_router(position_router)
router.include_router(struct_adm_position_router)
