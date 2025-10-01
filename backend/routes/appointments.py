from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from database import execute_query, get_db_connection
from schemas import Appointment

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

@router.get("/", response_model=List[Appointment])
async def get_appointments(
    date_from: Optional[date] = Query(None, description="시작 날짜"),
    date_to: Optional[date] = Query(None, description="종료 날짜"),
    department: Optional[str] = Query(None, description="진료과"),
    status: Optional[str] = Query(None, description="예약 상태"),
    limit: int = Query(50, description="조회할 예약 수")
):
    """
    예약 목록 조회 (필터링 가능)
    """
    sql = """
        SELECT a.*, p.name as patient_name, p.patient_no, p.phone
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE 1=1
    """
    params = []
    
    if date_from:
        sql += " AND DATE(a.appointment_date) >= %s"
        params.append(date_from)
    
    if date_to:
        sql += " AND DATE(a.appointment_date) <= %s"
        params.append(date_to)
    
    if department:
        sql += " AND a.department = %s"
        params.append(department)
    
    if status:
        sql += " AND a.status = %s"
        params.append(status)
    
    sql += " ORDER BY a.appointment_date ASC LIMIT %s"
    params.append(limit)
    
    results = execute_query(sql, tuple(params))
    
    if results is None:
        raise HTTPException(status_code=500, detail="예약 조회 중 오류가 발생했습니다")
    
    return results

@router.get("/today", response_model=List[Appointment])
async def get_today_appointments():
    """
    오늘의 예약 목록
    """
    sql = """
        SELECT a.*, p.name as patient_name, p.patient_no, p.phone
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE DATE(a.appointment_date) = CURDATE() AND a.status = '예약'
        ORDER BY a.appointment_date ASC
    """
    
    results = execute_query(sql)
    
    if results is None:
        raise HTTPException(status_code=500, detail="오늘 예약 조회 중 오류가 발생했습니다")
    
    return results

@router.get("/upcoming", response_model=List[Appointment])
async def get_upcoming_appointments(days: int = Query(7, description="조회할 일수")):
    """
    향후 예약 목록 (기본 7일)
    """
    sql = """
        SELECT a.*, p.name as patient_name, p.patient_no, p.phone
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.appointment_date >= NOW() 
        AND a.appointment_date <= DATE_ADD(NOW(), INTERVAL %s DAY)
        AND a.status = '예약'
        ORDER BY a.appointment_date ASC
    """
    
    results = execute_query(sql, (days,))
    
    if results is None:
        raise HTTPException(status_code=500, detail="예약 조회 중 오류가 발생했습니다")
    
    return results

@router.post("/")
async def create_appointment(appointment_data: dict):
    """
    새 예약 추가
    """
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
    
    try:
        cursor = connection.cursor()
        
        # 환자 존재 확인
        check_query = "SELECT COUNT(*) FROM patients WHERE patient_id = %s"
        cursor.execute(check_query, (appointment_data['patient_id'],))
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=400, detail="존재하지 않는 환자입니다")
        
        # 예약 추가
        insert_query = """
            INSERT INTO appointments 
            (patient_id, appointment_date, department, doctor_name, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            appointment_data['patient_id'],
            appointment_data['appointment_date'],
            appointment_data['department'],
            appointment_data['doctor_name'],
            appointment_data.get('status', '예약')
        ))
        
        connection.commit()
        
        # 생성된 예약 ID 반환
        appointment_id = cursor.lastrowid
        return {
            "appointment_id": appointment_id,
            "patient_id": appointment_data['patient_id'],
            "message": "예약 추가 성공"
        }
        
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"예약 추가 실패: {str(e)}")
    finally:
        cursor.close()
        connection.close()