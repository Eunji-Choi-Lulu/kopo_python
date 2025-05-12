# -*- coding: utf-8 -*-

# 1. 라이브러리 불러오기
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, inspect
import pymysql
from datetime import datetime

# 2. MySQL 연결 정보 (ngrok 정보 포함)
user = 'kopouser'
password = 'kopouser'
host = '0.tcp.jp.ngrok.io'
port = 15744  # 현재 ngrok에서 열려 있는 포트로 수정해야함
database = 'midterm'

# 3. 파라미터 테이블 조회용 연결
param_conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    db=database
)

# 4. 파라미터 테이블에서 경로 읽기
df_params = pd.read_sql("SELECT param_key, param_value FROM etl_param_table", param_conn)
param_dict = dict(zip(df_params['param_key'], df_params['param_value']))

customerUrl = param_dict['customer_path']
loanUrl = param_dict['loan_path']

# 5. CSV 파일 읽기
encoding = ["ms949", "utf-8"]
for i in range(len(encoding)):
    try:
        customerData = pd.read_csv(customerUrl, encoding=encoding[i])
        loanData = pd.read_csv(loanUrl, encoding=encoding[i])
        break
    except Exception as e:
        print(e, encoding[i])

# 6. SQLAlchemy 엔진 생성
myngine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

# 7. 데이터프레임을 테이블로 저장
tableList = ["customer_data", "loan_data"]
tableDf = [customerData, loanData]

for i in range(len(tableList)):
    tableName = tableList[i]
    dfName = tableDf[i]
    try:
        dfName.to_sql(name=tableName, con=myngine, if_exists='replace', index=False)
        print(f"{tableName} DB 입력 성공")
    except Exception as e:
        print(e)

# 8. 조인 쿼리 실행
joinQuery = """
SELECT A.*,
	   B.loan_type,
	   B.loan_amount,
	   B.loan_date
FROM (
	SELECT
		CUSTOMER_ID,
		NAME,
		GENDER,
		CASE WHEN SUBSTRING(BIRTH_DATE, 6, 3) = '010' THEN CONCAT(SUBSTRING(BIRTH_DATE, 1, 5), '10', SUBSTRING(BIRTH_DATE,9))
	         WHEN SUBSTRING(BIRTH_DATE, 6, 3) = '011' THEN CONCAT(SUBSTRING(BIRTH_DATE, 1, 5), '11', SUBSTRING(BIRTH_DATE,9))
	         WHEN SUBSTRING(BIRTH_DATE, 6, 3) = '012' THEN CONCAT(SUBSTRING(BIRTH_DATE, 1, 5), '12', SUBSTRING(BIRTH_DATE,9))
		     ELSE BIRTH_DATE END AS BIRTH_DATE,
		CASE WHEN SUBSTRING(JOIN_DATE, 6, 3) = '010' THEN CONCAT(SUBSTRING(JOIN_DATE, 1, 5), '10', SUBSTRING(JOIN_DATE,9))
	         WHEN SUBSTRING(JOIN_DATE, 6, 3) = '011' THEN CONCAT(SUBSTRING(JOIN_DATE, 1, 5), '11', SUBSTRING(JOIN_DATE,9))
	         WHEN SUBSTRING(JOIN_DATE, 6, 3) = '012' THEN CONCAT(SUBSTRING(JOIN_DATE, 1, 5), '12', SUBSTRING(JOIN_DATE,9))
		     ELSE JOIN_DATE END AS JOIN_DATE
	FROM customer_data
) A
LEFT JOIN
(
SELECT
	CUSTOMER_ID,
	LOAN_ID,
	LOAN_TYPE,
	LOAN_AMOUNT,
	CASE WHEN SUBSTRING(LOAN_DATE, 6, 3) = '010' THEN CONCAT(SUBSTRING(LOAN_DATE, 1, 5), '10', SUBSTRING(LOAN_DATE,9))
	     WHEN SUBSTRING(LOAN_DATE, 6, 3) = '011' THEN CONCAT(SUBSTRING(LOAN_DATE, 1, 5), '11', SUBSTRING(LOAN_DATE,9))
	     WHEN SUBSTRING(LOAN_DATE, 6, 3) = '012' THEN CONCAT(SUBSTRING(LOAN_DATE, 1, 5), '12', SUBSTRING(LOAN_DATE,9))
	     ELSE LOAN_DATE END AS LOAN_DATE
FROM loan_data
) B
ON A.customer_id = B.CUSTOMER_ID
WHERE LOAN_TYPE ='MORTGAGE'
AND LOAN_AMOUNT > 6000000
"""

Df = pd.read_sql_query(joinQuery, con=myngine)

# 9. TIME_TAG 컬럼 추가 및 mortgage_data로 저장
Df['TIME_TAG'] = datetime.now()
Df.to_sql(name='mortgage_data', con=myngine, if_exists='append', index=False)
print("데이터 DB 저장 완료")


