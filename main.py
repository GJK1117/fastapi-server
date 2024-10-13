from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis

app = FastAPI()

# 모든 출처에서의 요청을 허용하기 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# Redis 기본 엔드포인트 (샤드 0, 노드가 하나이므로 이 하나만 사용)
REDIS_PRIMARY_ENDPOINT = "study-mentor-link-redis.g0cwuy.ng.0001.apn2.cache.amazonaws.com"
REDIS_PORT = 6379

# Redis 클라이언트 초기화
redis_client = redis.StrictRedis(
    host=REDIS_PRIMARY_ENDPOINT,
    port=REDIS_PORT,
    decode_responses=True  # 이 옵션은 바이트 데이터를 문자열로 자동 변환합니다.
)

@app.get("/")
def read_root():
    # Redis에 데이터 쓰기
    redis_client.set("message", "Hello from Redis!")
    
    # Redis에서 데이터 읽기
    message = redis_client.get("message")
    
    return {"message": message}
