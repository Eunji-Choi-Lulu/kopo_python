# -*- coding: utf-8 -*-
"""Q5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GPCc0zRpRMV6WpNkAW1NnEGoM3q008QG
"""

# 'datasets' 라이브러리의 2.21.0 버전을 설치하는 명령어
!pip install datasets==2.21.0

# 웹 요청을 보내기 위한 requests 라이브러리 불러오기
import requests

# JSON 데이터를 다루기 위한 json 라이브러리 불러오기
import json

# 데이터 프레임 형태로 데이터를 처리하기 위한 pandas 라이브러리 불러오기
import pandas as pd

# Hugging Face의 Dataset 클래스를 사용하기 위한 불러오기
from datasets import Dataset

# Hugging Face Hub에 연결하여 모델이나 데이터셋을 업로드/다운로드할 수 있게 해주는 라이브러리 불러오기
import huggingface_hub

"""### JSON 형태의 행정 문서 대상 기계독해 데이터 (출처: AI허브 -> 한국어/텍스트 조회 -> "한국어 지식기반 관계데이터")"""

#url 불러오기
url = "https://drive.google.com/uc?export=download&id=1JehPjKhyw9NlVdoKBv7ZtxZLqaEjN7H9"

# 예외처리 시도 + 타켓URL에 데이터 요청
try:
    response = requests.get (url = url)
except Exception as e:
    print(e)

# 응답받은 JSON 텍스트 데이터를 Python의 딕셔너리 형태로 변환
original_data = json.loads(response.text)
print(original_data)

#원본데이터의 키 확인하기
original_data.keys()

#데이터의 갯수 확인
len( original_data["data"] )

#모든 데이터 출력
datas = original_data["data"]
datas

"""### 데이터를 alpaca 포맷 (instruction, input, ouput) 형태로 수집"""

#모든 질문을 담을 리스트 초기화
column1 = []
column2 = []
column3 = []

#datas리스트에 있는 각 요소를 하나씩 반복
for eachData in datas:
    #각 문서의 paragraph 리스트 안에 있는 문단 반복
    for eachParagraphs in eachData["paragraphs"]:
        #문단 내 'qas'키에 해당하는 질문-답변 데이터 추출
        qasData = eachParagraphs["qas"]
        for eachQas in qasData:
            #1. 컬럼1 추출
            column1.append(eachQas["question"])
            #2.컬럼2 추출
            clueText = eachQas["answers"]["clue_text"]
            options = eachQas["answers"]["options"]
            #+연산자는 문자열끼리만 연결할 수 있음
            optionText = "\n".join(options) #options리스트를 줄바꿈으로 연결
            column2.append (clueText + "\noptions\n" + optionText)
            #3. 컬럼3 추출
            column3.append(eachQas["answers"]["text"])


#DataFrame형식으로 묶기
finalDf = pd.DataFrame(zip(column1,column2,column3))

#컬럼이름 지정
finalDf.columns =["instruction" , "input", "output"]
finalDf

#허깅페이스에 업로드
dataset = Dataset.from_pandas(finalDf)
huggingface_hub.login("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")
dataset.push_to_hub("EunjiChoi/finalDs")