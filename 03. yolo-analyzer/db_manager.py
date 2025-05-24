import pymysql
from datetime import datetime

# MySQL 연결 설정
def get_connection():
    return pymysql.connect(
        host='0.tcp.jp.ngrok.io',   # ngrok 터널링 주소
        port=12094,                 # ngrok 포트
        user='root',
        password='Kopo1234##',
        database='thermal_monitor',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 분석 결과를 DB에 저장
def insert_detection(timestamp, temperature, status, image_path):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO detection_log (timestamp, temperature, status, image_path)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (timestamp, temperature, status, image_path))
        conn.commit()
        print("DB 저장 성공")
    except Exception as e:
        print("DB 저장 실패:", e)
    finally:
        conn.close()

# 테스트용 실행 코드
if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_detection(now, 36.7, '정상', '/static/results/sample.jpg')