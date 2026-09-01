from fastapi import APIRouter

from .views import router as users_position_router

router = APIRouter(tags=["users_position"])

router.include_router(users_position_router)
