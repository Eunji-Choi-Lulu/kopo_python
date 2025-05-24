# Dockerfile

# 1. Python 기반 이미지
FROM python:3.10-slim

# 2. 필수 시스템 패키지 설치 (OpenCV용 libGL 등 포함)
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 코드 복사
COPY . /app

# 5. Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 6. 모델, 입력, 출력 디렉토리 보장
RUN mkdir -p input static/results

# 7. 실행 명령
CMD ["python3", "video_inference.py"]