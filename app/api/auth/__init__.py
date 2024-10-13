from fastapi import APIRouter
from app.api.auth.routers import router

api_router=APIRouter()
api_router.include_router(router, prefix="/auth", tags=["auth"])