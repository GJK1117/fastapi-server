from fastapi import APIRouter
from app.api.auth import api_router as auth_api_router

api_router=APIRouter()
api_router.include_router(auth_api_router)