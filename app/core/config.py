import os

# AWS Redis 관련 환경변수
# Redis 기본 엔드포인트 (샤드 0, 노드가 하나이므로 이 하나만 사용)
REDIS_PRIMARY_ENDPOINT=os.environ['REDIS_PRIMARY_ENDPOINT']
REDIS_PORT = 6379

# SMTP Protocol 관련 환경변수
smtp_username = os.environ['SMTP_USERNAME']
smtp_password = os.environ['SMTP_PASSWORD']