# Python 3.9 이미지를 기반으로 함
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /var/task

# 필요한 시스템 패키지 설치 (필요에 따라 추가)
# RUN apt-get update && apt-get install -y ...

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src
COPY lambda_function.py .

# Lambda가 호출할 핸들러 지정
CMD ["python", "-m", "awslambdaric", "lambda_function.lambda_handler"]
