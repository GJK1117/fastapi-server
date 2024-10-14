from fastapi import APIRouter
from app.api.chatbot.qa import router as qa_router

api_router = APIRouter()
api_router.include_router(qa_router, prefix="/question-answer", tags=["question-answer", "qa"])