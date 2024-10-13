from pydantic import BaseModel

# Email 요청 데이터 모델
class EmailRequest(BaseModel):
    email: str

# 인증 코드 확인 요청 데이터 모델
class VerificationRequest(BaseModel):
    email: str
    authnum: str