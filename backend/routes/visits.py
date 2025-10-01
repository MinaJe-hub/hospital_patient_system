from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from database import execute_query, get_db_connection
from schemas import Visit

router = APIRouter(prefix="/api/visits", tags=["visits"])

@router.get("/", response_model=List[Visit])
async def get_visits(
    date_from: Optional[date] = Query(None, description="시작 날짜"),
    date_to: Optional[date] = Query(None, description="종료 날짜"),
    department: Optional[str] = Query(None, description="진료과"),
    status: Optional[str] = Query(None, description="진료 상태"),
    limit: int = Query(50, description="조회할 진료 수")
):
    """
    진료 기록 조회 (필터링 가능)
    """
    sql = """
        SELECT v.*, p.name as patient_name, p.patient_no
        FROM visits v
        JOIN patients p ON v.patient_id = p.patient_id
        WHERE 1=1
    """
    params = []
    
    if date_from:
        sql += " AND DATE(v.visit_date) >= %s"
        params.append(date_from)
    
    if date_to:
        sql += " AND DATE(v.visit_date) <= %s"
        params.append(date_to)
    
    if department:
        sql += " AND v.department = %s"
        params.append(department)
    
    if status:
        sql += " AND v.status = %s"
        params.append(status)
    
    sql += " ORDER BY v.visit_date DESC LIMIT %s"
    params.append(limit)
    
    results = execute_query(sql, tuple(params))
    
    if results is None:
        raise HTTPException(status_code=500, detail="진료 기록 조회 중 오류가 발생했습니다")
    
    return results

@router.get("/today", response_model=List[Visit])
async def get_today_visits():
    """
    오늘의 진료 목록
    """
    sql = """
        SELECT v.*, p.name as patient_name, p.patient_no
        FROM visits v
        JOIN patients p ON v.patient_id = p.patient_id
        WHERE DATE(v.visit_date) = CURDATE()
        ORDER BY v.visit_date ASC
    """
    
    results = execute_query(sql)
    
    if results is None:
        raise HTTPException(status_code=500, detail="오늘 진료 조회 중 오류가 발생했습니다")
    
    return results

@router.get("/departments")
async def get_departments():
    """
    진료과 목록 조회
    """
    sql = """
        SELECT DISTINCT department 
        FROM visits 
        WHERE department IS NOT NULL
        ORDER BY department
    """
    
    results = execute_query(sql)
    
    if results is None:
        raise HTTPException(status_code=500, detail="진료과 목록 조회 중 오류가 발생했습니다")
    
    return [row['department'] for row in results]

@router.post("/")
async def create_visit(visit_data: dict):
    """
    새 진료 기록 추가
    """
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
    
    try:
        cursor = connection.cursor()
        
        # 환자 존재 확인
        check_query = "SELECT COUNT(*) FROM patients WHERE patient_id = %s"
        cursor.execute(check_query, (visit_data['patient_id'],))
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=400, detail="존재하지 않는 환자입니다")
        
        # 진료 기록 추가
        insert_query = """
            INSERT INTO visits 
            (patient_id, visit_date, department, doctor_name, diagnosis, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            visit_data['patient_id'],
            visit_data['visit_date'],
            visit_data['department'],
            visit_data['doctor_name'],
            visit_data['diagnosis'],
            visit_data.get('status', '완료')
        ))
        
        connection.commit()
        
        # 생성된 진료 ID 반환
        visit_id = cursor.lastrowid
        return {
            "visit_id": visit_id,
            "patient_id": visit_data['patient_id'],
            "message": "진료 기록 추가 성공"
        }
        
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"진료 기록 추가 실패: {str(e)}")
    finally:
        cursor.close()
        connection.close()