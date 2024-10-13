from redis import StrictRedis
from .core.config import REDIS_PRIMARY_ENDPOINT, REDIS_PORT

# Redis 클라이언트 초기화
try: 
    redis_client_email_auth = StrictRedis(
        host=REDIS_PRIMARY_ENDPOINT,
        port=REDIS_PORT,
        db=1
    )
    redis_client_email_auth.ping()
    print("이메일 인증 Redis 연결 성공")
except Exception as e:
    print(f"이메일 인증 Redis 연결 실패: {e}")
    
# Redis 클라이언트 초기화
try: 
    redis_client_retriever = StrictRedis(
        host=REDIS_PRIMARY_ENDPOINT,
        port=REDIS_PORT,
        db=0
    )
    redis_client_retriever.ping()
    print("retriever Redis 연결 성공")
except Exception as e:
    print(f"retriever Redis 연결 실패: {e}")