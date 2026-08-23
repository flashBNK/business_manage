from api.v1.account.routers import router as account_router
from api.v1.employee.routers import router as employee_router
from api.v1.user.routers import router as user_router
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")
router.include_router(user_router)
router.include_router(account_router)
router.include_router(employee_router)
