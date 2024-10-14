from fastapi import APIRouter
from app.api.auth.email import router as email_router
from app.api.auth.num import router as num_router

api_router=APIRouter()
api_router.include_router(email_router, prefix="/email", tags=["auth", "email"])
api_router.include_router(num_router, prefix="/num", tags=["auth", "num"])