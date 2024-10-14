from fastapi import APIRouter
from app.api.upload.image import router as image_router
from app.api.upload.images import router as images_router
from app.api.upload.pdf import router as pdf_router

api_router = APIRouter()
api_router.include_router(image_router, prefix="/image", tags=["image"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
api_router.include_router(pdf_router, prefix="/pdf", tags=["pdf"])