# -*- coding: utf-8 -*-
"""커스텀모델생성(영상제어).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LzEzAQlxZu1ObSUtXbO4kIgmrPON5jvq
"""

!pip install ultralytics

#구글드라이브에 저장
from google.colab import drive
drive.mount("/content/gdrive")

"""## 모델 학습시키기"""

# 내가 학습시킨 모델
trained_model = YOLO("/content/gdrive/MyDrive/중간고사/객체인식/Africa-Transport-2/runs/detect/train/weights/best.pt")

"""###한개 이미지 예측해보기

###영상 제어
"""

from IPython.display import Audio, display
import cv2
from ultralytics import YOLO


#YOLO 모델 로드 (학습된 모델 경로 사용)
model = YOLO("/content/gdrive/MyDrive/중간고사/객체인식/Africa-Transport-2/runs/detect/train/weights/best.pt")

# 불러올 경로
video_path = '/content/gdrive/MyDrive/중간고사/객체인식/Africa-Transport-2/test video/testVideo_1.mp4'

# 프레임만 저장할 경로
output_video_path = '/content/gdrive/MyDrive/중간고사/객체인식/Africa-Transport-2/test video/reconstructed_testVideo_1.mp4'

# mp4파일을 불러오는 것
# 비디오 캡처 객체 생성
capture = cv2.VideoCapture(video_path)

# 프레임 크기 가져오기
frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 비디오 라이터 객체 생성
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30  # 저장할 동영상의 프레임 속도 (FPS): 30 이 유럽 표준

video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# 바운딩 박스 설정
GREEN = (0, 255, 0)
CONFIDENCE_THRESHOLD = 0.6

# 프레임을 하나씩 읽어와서 바로 새로운 MP4 파일에 저장
while capture.isOpened():
    ret, frame = capture.read()
    if ret:
        detection = model(frame)[0]
        boxInfos = detection.boxes.data.tolist()
        for i in range (0,len(boxInfos)):
            eachbox = boxInfos[i]
            xmin = int(eachbox[0])
            ymin = int(eachbox[1])
            xmax = int(eachbox[2])
            ymax = int(eachbox[3])
            confidence = eachbox[4]
            className = eachbox[5]
            realName = model.names[int(className)] ##인식한 class name

            # 정확도가 0.6보다 큰 경우에만 ractangle을 그릴 수 있도록
            # cv2.putText : 텍스트를 넣고 싶을 때

            if (confidence > 0.6):
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 3)
                cv2.putText (frame, realName,  (xmin,ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 2)

                # display(Audio(sound_path, autoplay=True))
        # 프레임을 비디오에 저장
        video_writer.write(frame)
    else:
        break

# 비디오 캡처 및 라이터 객체 해제
capture.release()
video_writer.release()

from moviepy.editor import AudioFileClip

audio = AudioFileClip("/content/gdrive/MyDrive/중간고사/객체인식/자동차경적소리.mp3")
print("Duration:", audio.duration)