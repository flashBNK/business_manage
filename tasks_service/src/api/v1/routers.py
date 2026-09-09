from fastapi import APIRouter

from .task.routers import router as task_router

router = APIRouter(prefix="/api/v1")
router.include_router(task_router)
