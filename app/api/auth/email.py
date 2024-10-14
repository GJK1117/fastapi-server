from fastapi import HTTPException, Depends, APIRouter
import smtplib
from email.mime.text import MIMEText
import random
from app.db import redis_client_auth
from app.core.firebase import token_required
from app.core.config import smtp_username, smtp_password
from app.schemas.email_schemas import EmailRequest

router = APIRouter()

# 이메일로 인증 코드를 보내는 비동기 함수
@router.post("/", dependencies=[Depends(token_required)])
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