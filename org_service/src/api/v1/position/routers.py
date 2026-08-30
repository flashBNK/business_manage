from fastapi import APIRouter

from .views import router as position_router

router = APIRouter(tags=["position"])

router.include_router(position_router)
