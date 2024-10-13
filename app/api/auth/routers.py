from fastapi import HTTPException, Depends, APIRouter
import smtplib
from email.mime.text import MIMEText
import random
from app.db import redis_client_auth
from app.core.firebase import token_required
from app.core.config import smtp_username, smtp_password
from app.schemas.email_schemas import EmailRequest, VerificationRequest

router = APIRouter()

# 이메일로 인증 코드를 보내는 비동기 함수
@router.post("/email", dependencies=[Depends(token_required)])
async def send_verification_code(email_request: EmailRequest):
    email = email_request.email

    # email이 없는 경우 예외 반환
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # 6자리 난수 생성
    code = '{:06d}'.format(random.randint(0, 999999))

    # Redis에 이메일-코드 저장, TTL 5분
    redis_client_auth.setex(email, 300, code)

    # SMTP 서버 설정
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # 이메일 메시지 구성
    msg = MIMEText(f'Your verification code is: {code}')
    msg['Subject'] = 'Study-mentor verification code'
    msg['From'] = 'study-mentor@gmail.com'
    msg['To'] = email

    try:
        # SMTP 서버를 통해 메일 전송
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, [email], msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "Verification code sent successfully"}

# 인증 코드를 검증하는 비동기 함수
@router.post("/num", dependencies=[Depends(token_required)])
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