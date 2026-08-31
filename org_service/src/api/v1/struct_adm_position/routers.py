from fastapi import APIRouter

from .views import router as struct_adm_position_router

router = APIRouter(tags=["struct_adm_position"])

router.include_router(struct_adm_position_router)
