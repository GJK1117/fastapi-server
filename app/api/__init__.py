from fastapi import APIRouter
from app.api.auth import api_router as auth_api_router
from app.api.chatbot import api_router as chatbot_api_router
from app.api.feedback import api_router as feedback_api_router
from app.api.upload import api_router as upload_api_router

api_router=APIRouter()
api_router.include_router(auth_api_router, prefix="/auth", tags=["auth"])
api_router.include_router(chatbot_api_router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(feedback_api_router, prefix="/feedback", tags=["feedback"])
api_router.include_router(upload_api_router, prefix="/upload", tags=["upload"])
