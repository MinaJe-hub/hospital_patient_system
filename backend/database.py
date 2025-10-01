import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def get_db_connection():
    """데이터베이스 연결 생성"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        return connection
    except Error as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def execute_query(query, params=None):
    """SELECT 쿼리 실행"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"쿼리 실행 오류: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def execute_single_query(query, params=None):
    """단일 결과 반환 쿼리"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"쿼리 실행 오류: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()