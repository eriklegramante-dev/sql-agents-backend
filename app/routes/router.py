from fastapi import APIRouter

from app.routes.create.user.route import router as create_router
from app.routes.create.admin.route import router as create_admin_router
from app.routes.auth.route import router as auth_router
from app.routes.read.router import router as read_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/api/v1", tags=["Auth"])

api_router.include_router(create_admin_router, prefix="/api/v1", tags=["Admin"])

api_router.include_router(create_router, prefix="/api/v1", tags=["Users"])

api_router.include_router(read_router, prefix="/api/v1", tags=["Read"])