from fastapi import APIRouter
from app.api.auth import api_router as auth_api_router
from app.api.chatbot import api_router as chatbot_api_router

api_router=APIRouter()
api_router.include_router(auth_api_router, prefix="/auth", tags=["auth"])
api_router.include_router(chatbot_api_router, prefix="/chatbot", tags=["chatbot"])
