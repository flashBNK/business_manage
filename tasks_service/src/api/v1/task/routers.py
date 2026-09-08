from fastapi import APIRouter

from .views import router as task_router

router = APIRouter(tags=["task"])

router.include_router(task_router)
