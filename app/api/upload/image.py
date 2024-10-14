from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.firebase import token_required

router = APIRouter()

@router.post("/", dependencies=[Depends(token_required)])
async def image():
    return JSONResponse(content={"message": "good"}, status_code=200)