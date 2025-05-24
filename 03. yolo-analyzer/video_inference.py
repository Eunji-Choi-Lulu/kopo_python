from db_manager import insert_detection
from datetime import datetime

import cv2
from ultralytics import YOLO
import os

model_path = 'best.pt'
input_video = 'input/test_video.mp4'
output_video = 'static/results/result.mp4'

# 모델 로드
model = YOLO(model_path)

# 입력 영상 열기
capture = cv2.VideoCapture(input_video)
frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = capture.get(cv2.CAP_PROP_FPS)

# 출력 디렉토리 생성
os.makedirs('static/results', exist_ok=True)

# 비디오 저장 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

# 추론 실행
while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(rgb_frame, imgsz=640, conf=0.6)[0]

    for box in results.boxes.data.tolist():
        xmin, ymin, xmax, ymax, conf, cls = box
        if conf > 0.6:
            class_name = model.names[int(cls)]

            # 감지된 클래스 출력
            print("Detected class:", class_name)

            # 바운딩박스 및 텍스트 표시
            xmin, ymin, xmax, ymax = map(int, [xmin, ymin, xmax, ymax])
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
            cv2.putText(frame, f"{class_name} {conf:.2f}", (xmin, max(ymin - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # DB 기록: 'abnormal'일 때만
            if class_name.lower() == 'abnormal':
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_detection(timestamp, 0.0, '이상', output_video)
                print(f"감지된 클래스: {class_name}")

    video_writer.write(frame)

capture.release()
video_writer.release()

print("분석 완료")
print("모델 클래스 목록:", model.names)
