import csv
import requests
import json
from datetime import datetime
import time

# API 기본 URL
BASE_URL = "http://localhost:8000"

# 환자 번호와 ID 매핑 저장
patient_mapping = {}

def read_csv(filename):
    """CSV 파일 읽기"""
    data = []
    with open(f'data/{filename}', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

def upload_patients():
    """환자 데이터 업로드"""
    print("\n=== 환자 데이터 업로드 시작 ===")
    patients = read_csv('patients.csv')
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for patient in patients:
        # 먼저 환자가 이미 존재하는지 확인
        try:
            response = requests.get(
                f"{BASE_URL}/api/patients/search",
                params={"query": patient['patient_no']}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result:
                    # 환자가 이미 있으면 ID 저장만 하고 건너뜀
                    patient_mapping[patient['patient_no']] = result[0]['patient_id']
                    print(f"○ {patient['name']} ({patient['patient_no']}) - 이미 존재")
                    skip_count += 1
                    continue
        except:
            pass
        
        # 새로운 환자 추가
        patient_data = {
            "patient_no": patient['patient_no'],
            "name": patient['name'],
            "birth_date": patient['birth_date'],
            "gender": patient['gender'],
            "phone": patient['phone']
        }
        
        try:
            # POST 요청으로 환자 추가
            response = requests.post(
                f"{BASE_URL}/api/patients/",
                json=patient_data
            )
            
            if response.status_code == 200:
                result = response.json()
                patient_mapping[patient['patient_no']] = result['patient_id']
                print(f"✓ {patient['name']} ({patient['patient_no']}) - 추가 성공")
                success_count += 1
            else:
                print(f"✗ {patient['name']} - 오류: {response.text}")
                fail_count += 1
                
        except Exception as e:
            print(f"✗ {patient['name']} - 오류: {e}")
            fail_count += 1
    
    print(f"\n환자 업로드 완료: 추가 {success_count}명, 기존 {skip_count}명, 실패 {fail_count}명")
    return patient_mapping

def upload_visits():
    """진료 기록 업로드"""
    print("\n=== 진료 기록 업로드 시작 ===")
    visits = read_csv('visits.csv')
    
    success_count = 0
    fail_count = 0
    
    for visit in visits:
        # patient_no를 patient_id로 변환
        patient_id = patient_mapping.get(visit['patient_no'])
        
        if not patient_id:
            # 환자를 찾을 수 없으면 검색해서 ID 찾기
            try:
                response = requests.get(
                    f"{BASE_URL}/api/patients/search",
                    params={"query": visit['patient_no']}
                )
                if response.status_code == 200:
                    result = response.json()
                    if result:
                        patient_id = result[0]['patient_id']
                        patient_mapping[visit['patient_no']] = patient_id
                    else:
                        print(f"✗ 환자번호 {visit['patient_no']} 찾을 수 없음")
                        fail_count += 1
                        continue
            except:
                print(f"✗ 환자번호 {visit['patient_no']} 검색 실패")
                fail_count += 1
                continue
        
        visit_data = {
            "patient_id": patient_id,
            "visit_date": visit['visit_date'],
            "department": visit['department'],
            "doctor_name": visit['doctor_name'],
            "diagnosis": visit['diagnosis'],
            "status": visit['status']
        }
        
        try:
            # POST 요청으로 진료 기록 추가
            response = requests.post(
                f"{BASE_URL}/api/visits/",
                json=visit_data
            )
            
            if response.status_code == 200:
                print(f"✓ {visit['patient_no']} - {visit['diagnosis']}")
                success_count += 1
            else:
                print(f"✗ 진료 기록 오류: {response.text}")
                fail_count += 1
            
        except Exception as e:
            print(f"✗ 진료 기록 오류: {e}")
            fail_count += 1
    
    print(f"\n진료 기록 업로드 완료: 성공 {success_count}건, 실패 {fail_count}건")

def upload_appointments():
    """예약 데이터 업로드"""
    print("\n=== 예약 데이터 업로드 시작 ===")
    appointments = read_csv('appointments.csv')
    
    success_count = 0
    fail_count = 0
    
    for appointment in appointments:
        # patient_no를 patient_id로 변환
        patient_id = patient_mapping.get(appointment['patient_no'])
        
        if not patient_id:
            # 환자를 찾을 수 없으면 검색해서 ID 찾기
            try:
                response = requests.get(
                    f"{BASE_URL}/api/patients/search",
                    params={"query": appointment['patient_no']}
                )
                if response.status_code == 200:
                    result = response.json()
                    if result:
                        patient_id = result[0]['patient_id']
                        patient_mapping[appointment['patient_no']] = patient_id
                    else:
                        print(f"✗ 환자번호 {appointment['patient_no']} 찾을 수 없음")
                        fail_count += 1
                        continue
            except:
                print(f"✗ 환자번호 {appointment['patient_no']} 검색 실패")
                fail_count += 1
                continue
        
        appointment_data = {
            "patient_id": patient_id,
            "appointment_date": appointment['appointment_date'],
            "department": appointment['department'],
            "doctor_name": appointment['doctor_name'],
            "status": appointment['status']
        }
        
        try:
            # POST 요청으로 예약 추가
            response = requests.post(
                f"{BASE_URL}/api/appointments/",
                json=appointment_data
            )
            
            if response.status_code == 200:
                print(f"✓ {appointment['patient_no']} - {appointment['status']}")
                success_count += 1
            else:
                print(f"✗ 예약 오류: {response.text}")
                fail_count += 1
            
        except Exception as e:
            print(f"✗ 예약 오류: {e}")
            fail_count += 1
    
    print(f"\n예약 업로드 완료: 성공 {success_count}건, 실패 {fail_count}건")

def test_api_connection():
    """API 연결 테스트"""
    print("=== API 연결 테스트 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API 서버 연결 성공")
            return True
        else:
            print(f"✗ API 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API 서버 연결 실패: {e}")
        print("main.py가 실행 중인지 확인하세요!")
        return False

def check_upload_results():
    """업로드 결과 확인"""
    print("\n=== 업로드 결과 확인 ===")
    
    try:
        # 통계 확인
        response = requests.get(f"{BASE_URL}/api/patients/stats/today")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n[데이터베이스 통계]")
            print(f"전체 환자 수: {stats.get('total_patients', 0)}명")
            print(f"오늘 진료: {stats.get('today_visits', 0)}건")
            print(f"오늘 예약: {stats.get('today_appointments', 0)}건")
            print(f"대기 중인 환자: {stats.get('waiting_patients', 0)}명")
        
        # 샘플 환자 검색
        print(f"\n[환자 검색 테스트]")
        test_names = ['김', '이', '박']
        for name in test_names:
            response = requests.get(
                f"{BASE_URL}/api/patients/search",
                params={"query": name}
            )
            if response.status_code == 200:
                results = response.json()
                print(f"'{name}'으로 검색: {len(results)}명 발견")
        
        # 특정 환자 상세 조회
        print(f"\n[환자 상세 조회 테스트]")
        response = requests.get(
            f"{BASE_URL}/api/patients/search",
            params={"query": "P2024104"}
        )
        if response.status_code == 200:
            results = response.json()
            if results:
                patient = results[0]
                print(f"환자번호: {patient['patient_no']}")
                print(f"이름: {patient['name']}")
                print(f"성별: {patient['gender']}")
                print(f"진료 횟수: {patient.get('visit_count', 0)}회")
                
    except Exception as e:
        print(f"결과 확인 오류: {e}")

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("병원 CSV 데이터 업로드 스크립트")
    print("=" * 50)
    
    # 1. API 연결 확인
    if not test_api_connection():
        print("\n먼저 main.py를 실행해주세요!")
        print("터미널에서: python main.py")
        return
    
    print("\n데이터 업로드를 시작하시겠습니까? (y/n): ", end="")
    if input().lower() != 'y':
        print("업로드 취소됨")
        return
    
    # 2. 환자 데이터 업로드
    patient_mapping = upload_patients()
    
    # 3. 진료 기록 업로드
    if patient_mapping:
        time.sleep(1)  # 서버 부하 방지
        upload_visits()
    
    # 4. 예약 데이터 업로드
    if patient_mapping:
        time.sleep(1)  # 서버 부하 방지
        upload_appointments()
    
    # 5. 결과 확인
    time.sleep(2)
    check_upload_results()
    
    print("\n" + "=" * 50)
    print("업로드 완료!")
    print("브라우저에서 확인:")
    print("- API 문서: http://localhost:8000/docs")
    print("- 환자 검색 테스트: http://localhost:8000/api/patients/search?query=김")
    print("=" * 50)

if __name__ == "__main__":
    main()