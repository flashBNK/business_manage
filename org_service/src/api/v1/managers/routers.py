from fastapi import APIRouter

from .views import router as users_position_router

router = APIRouter(tags=["managers"])

router.include_router(users_position_router)
