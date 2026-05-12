from fastapi import APIRouter

from app.routes.auth.route import router as auth_router

from app.routes.create.user.route import (
    router as create_router,
)

from app.routes.create.admin.route import (
    router as create_admin_router,
)

from app.routes.delete.user.route import (
    router as delete_user_router,
)


api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["Auth"],
)

api_router.include_router(
    create_admin_router,
    prefix="/api/v1",
    tags=["Admin"],
)

api_router.include_router(
    create_router,
    prefix="/api/v1",
    tags=["Users"],
)

api_router.include_router(
    delete_user_router,
    prefix="/api/v1",
    tags=["Delete Users"],
)