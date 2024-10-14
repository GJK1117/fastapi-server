from fastapi import HTTPException, Depends, APIRouter
from app.db import redis_client_auth
from app.core.firebase import token_required
from app.schemas.email_schemas import VerificationRequest

router = APIRouter()

# 인증 코드를 검증하는 비동기 함수
@router.post("/", dependencies=[Depends(token_required)])
async def verify_code(verification_request: VerificationRequest):
    email = verification_request.email
    user_code = verification_request.authnum

    # email 또는 authnum이 없는 경우 예외 반환
    if not email or not user_code:
        raise HTTPException(status_code=400, detail="Email or verification code is missing")

    # Redis에서 저장된 인증 코드 가져오기
    stored_code = redis_client_auth.get(email)

    # 인증 코드가 없으면 예외 반환
    if not stored_code:
        raise HTTPException(status_code=400, detail="Email with expired or invalid credentials")

    # Redis에 저장된 인증 코드를 비교
    stored_code = stored_code.decode('utf-8')
    if user_code != stored_code:
        raise HTTPException(status_code=400, detail="Mismatched credentials")

    # 인증 완료 후 Redis에서 이메일 정보 삭제
    redis_client_auth.delete(email)

    return {"message": "Verification is complete"}