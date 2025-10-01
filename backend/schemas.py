from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# 환자 스키마
class Patient(BaseModel):
    patient_id: int
    patient_no: str
    name: str
    birth_date: Optional[date]
    gender: Optional[str]
    phone: Optional[str]
    created_at: Optional[datetime]

class PatientSearch(BaseModel):
    """환자 검색 응답"""
    patient_id: int
    patient_no: str
    name: str
    birth_date: Optional[date]
    gender: Optional[str]
    phone: Optional[str]
    visit_count: Optional[int] = 0
    last_visit_date: Optional[datetime] = None

# 진료 스키마
class Visit(BaseModel):
    visit_id: int
    patient_id: int
    visit_date: datetime
    department: Optional[str]
    doctor_name: Optional[str]
    diagnosis: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]

# 예약 스키마
class Appointment(BaseModel):
    appointment_id: int
    patient_id: int
    appointment_date: datetime
    department: Optional[str]
    doctor_name: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]

# 환자 상세 정보 (진료 기록, 예약 포함)
class PatientDetail(BaseModel):
    patient: Patient
    visits: List[Visit]
    appointments: List[Appointment]
    
# 검색 요청
class SearchRequest(BaseModel):
    query: str  # 환자명 또는 환자번호