from fastapi import APIRouter

from .views import router as structure_router

router = APIRouter(tags=["structure"])

router.include_router(structure_router)
