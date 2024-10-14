from fastapi import APIRouter
from app.api.feedback.route import router as default_router

api_router = APIRouter()
api_router.include_router(default_router)