from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import execute_query, execute_single_query, get_db_connection
from schemas import Patient, PatientSearch, PatientDetail, Visit, Appointment

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.get("/search", response_model=List[PatientSearch])
async def search_patients(query: str = Query(..., description="환자명 또는 환자번호")):
    """
    환자 검색 (이름 또는 환자번호로 검색)
    - 숫자만 입력: 환자번호로 검색
    - 문자 포함: 환자명으로 검색
    """
    
    # 검색어가 비어있으면 에러
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
    
    # 검색어 앞뒤 공백 제거
    search_term = query.strip()
    
    # 숫자로만 구성되어 있으면 환자번호로 검색
    if search_term.isdigit() or search_term.startswith('P'):
        sql = """
            SELECT 
                p.patient_id,
                p.patient_no,
                p.name,
                p.birth_date,
                p.gender,
                p.phone,
                p.created_at,
                COUNT(DISTINCT v.visit_id) as visit_count,
                MAX(v.visit_date) as last_visit_date
            FROM patients p
            LEFT JOIN visits v ON p.patient_id = v.patient_id
            WHERE p.patient_no LIKE %s
            GROUP BY p.patient_id
            ORDER BY p.name
        """
        params = (f"%{search_term}%",)
    else:
        # 문자가 포함되어 있으면 환자명으로 검색
        sql = """
            SELECT 
                p.patient_id,
                p.patient_no,
                p.name,
                p.birth_date,
                p.gender,
                p.phone,
                p.created_at,
                COUNT(DISTINCT v.visit_id) as visit_count,
                MAX(v.visit_date) as last_visit_date
            FROM patients p
            LEFT JOIN visits v ON p.patient_id = v.patient_id
            WHERE p.name LIKE %s
            GROUP BY p.patient_id
            ORDER BY p.name
            LIMIT 50
        """
        params = (f"%{search_term}%",)
    
    results = execute_query(sql, params)
    
    if results is None:
        raise HTTPException(status_code=500, detail="데이터베이스 조회 중 오류가 발생했습니다")
    
    if not results:
        return []
    
    return results

@router.get("/{patient_id}", response_model=PatientDetail)
async def get_patient_detail(patient_id: int):
    """
    환자 상세 정보 조회 (진료 기록, 예약 포함)
    """
    
    # 환자 기본 정보 조회
    patient_sql = """
        SELECT * FROM patients WHERE patient_id = %s
    """
    patient = execute_single_query(patient_sql, (patient_id,))
    
    if not patient:
        raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다")
    
    # 진료 기록 조회
    visits_sql = """
        SELECT * FROM visits 
        WHERE patient_id = %s 
        ORDER BY visit_date DESC
    """
    visits = execute_query(visits_sql, (patient_id,))
    
    # 예약 정보 조회
    appointments_sql = """
        SELECT * FROM appointments 
        WHERE patient_id = %s AND status != '취소'
        ORDER BY appointment_date ASC
    """
    appointments = execute_query(appointments_sql, (patient_id,))
    
    return {
        "patient": patient,
        "visits": visits or [],
        "appointments": appointments or []
    }

@router.get("/", response_model=List[Patient])
async def get_all_patients(
    limit: int = Query(20, description="조회할 환자 수"),
    offset: int = Query(0, description="시작 위치")
):
    """
    전체 환자 목록 조회 (페이징)
    """
    sql = """
        SELECT * FROM patients 
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    
    results = execute_query(sql, (limit, offset))
    
    if results is None:
        raise HTTPException(status_code=500, detail="데이터베이스 조회 중 오류가 발생했습니다")
    
    return results

@router.get("/stats/today")
async def get_today_stats():
    """
    오늘의 통계 (대시보드용)
    """
    stats_sql = """
        SELECT 
            (SELECT COUNT(*) FROM visits WHERE DATE(visit_date) = CURDATE()) as today_visits,
            (SELECT COUNT(*) FROM appointments WHERE DATE(appointment_date) = CURDATE() AND status = '예약') as today_appointments,
            (SELECT COUNT(*) FROM patients) as total_patients,
            (SELECT COUNT(*) FROM visits WHERE status = '대기') as waiting_patients
    """
    
    result = execute_single_query(stats_sql)
    
    if result is None:
        raise HTTPException(status_code=500, detail="통계 조회 중 오류가 발생했습니다")
    
    return result

@router.post("/")
async def create_patient(patient_data: dict):
    """
    새 환자 등록
    """
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
    
    try:
        cursor = connection.cursor()
        
        # 중복 체크
        check_query = "SELECT COUNT(*) FROM patients WHERE patient_no = %s"
        cursor.execute(check_query, (patient_data['patient_no'],))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="이미 존재하는 환자번호입니다")
        
        # 환자 추가
        insert_query = """
            INSERT INTO patients (patient_no, name, birth_date, gender, phone)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            patient_data['patient_no'],
            patient_data['name'],
            patient_data['birth_date'],
            patient_data['gender'],
            patient_data['phone']
        ))
        
        connection.commit()
        
        # 생성된 환자 정보 반환
        patient_id = cursor.lastrowid
        return {
            "patient_id": patient_id,
            "patient_no": patient_data['patient_no'],
            "name": patient_data['name'],
            "message": "환자 등록 성공"
        }
        
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"환자 등록 실패: {str(e)}")
    finally:
        cursor.close()
        connection.close()