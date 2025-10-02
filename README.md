# 🏥 병원 환자 조회 시스템 (Hospital Patient Management System)

환자 관리 시스템으로, 환자 정보 조회, 진료 기록 관리, 예약 관리 기능을 제공하는 웹 애플리케이션입니다.

## 📋 목차

- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [시스템 아키텍처](#-시스템-아키텍처)
- [설치 방법](#-설치-방법)
- [실행 방법](#-실행-방법)
- [API 문서](#-api-문서)
- [데이터베이스 구조](#-데이터베이스-구조)
- [프로젝트 구조](#-프로젝트-구조)
- [스크린샷](#-스크린샷)
- [개발 가이드](#-개발-가이드)
- [문제 해결](#-문제-해결)

## ✨ 주요 기능

### 1. 대시보드
- **실시간 통계**: 전체 환자 수, 오늘 진료, 예약 현황, 대기 환자
- **최근 진료 현황**: 당일 진료 활동 실시간 모니터링
- **빠른 환자 검색**: 헤더의 빠른 검색 기능

### 2. 환자 관리
- **환자 검색**: 이름, 환자번호로 빠른 검색
- **환자 상세 정보**: 기본 정보, 진료 이력, 예약 현황 통합 조회
- **신규 환자 등록**: 환자 정보 신규 등록 (환자번호 자동 생성)

### 3. 진료 관리
- **진료 기록 등록**: 새 진료 기록 추가
- **진료 이력 조회**: 환자별 과거 진료 기록 확인
- **진료 상태 관리**: 대기/진료중/완료 상태 관리

### 4. 예약 관리
- **예약 등록**: 새 예약 추가
- **예약 현황 조회**: 환자별 예약 목록 확인
- **예약 상태 관리**: 예약/완료/취소 상태 관리

## 🛠 기술 스택

### Backend
- **Python 3.8+**
- **FastAPI** - 고성능 웹 프레임워크
- **MySQL** - 관계형 데이터베이스
- **Uvicorn** - ASGI 서버
- **Pydantic** - 데이터 검증

### Frontend
- **Vanilla JavaScript** - 프레임워크 없는 순수 자바스크립트
- **HTML5/CSS3** - 반응형 디자인
- **REST API** - 백엔드 통신

## 🏗 시스템 아키텍처

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend  │────▶│   Backend    │────▶│   Database   │
│  (HTML/JS)  │     │  (FastAPI)   │     │    (MySQL)   │
└─────────────┘     └──────────────┘     └──────────────┘
        ↓                   ↓                     ↓
   [웹 브라우저]      [REST API]            [데이터 저장]
```

## 📦 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- MySQL 5.7 이상
- Git

### 2. 저장소 클론
```bash
git clone https://github.com/yourusername/hospital-patient-system.git
cd hospital-patient-system
```

### 3. Python 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
cd backend
pip install -r requirements.txt
```

### 4. MySQL 데이터베이스 설정

```sql
-- MySQL 접속 후 실행
CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_db;

-- 환자 테이블
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_no VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    birth_date DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient_no (patient_no),
    INDEX idx_name (name)
);

-- 진료 테이블
CREATE TABLE visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    visit_date DATETIME NOT NULL,
    department VARCHAR(30),
    doctor_name VARCHAR(30),
    diagnosis TEXT,
    status VARCHAR(10) DEFAULT '완료',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    INDEX idx_visit_date (visit_date),
    INDEX idx_patient_id (patient_id)
);

-- 예약 테이블
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    department VARCHAR(30),
    doctor_name VARCHAR(30),
    status VARCHAR(10) DEFAULT '예약',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_patient_id (patient_id)
);
```

### 5. 환경변수 설정

`backend/.env` 파일 생성:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=hospital_db
DB_PORT=3306
```

## 🚀 실행 방법

### 1. Backend 서버 실행
```bash
cd backend
python main.py
```
서버가 `http://localhost:8000`에서 실행됩니다.

### 2. 샘플 데이터 업로드 (선택사항)
새 터미널 창에서:
```bash
cd backend
python upload_csv_to_api.py
```
- 100명의 환자 데이터
- 113건의 진료 기록
- 49건의 예약 데이터가 자동으로 업로드됩니다.

### 3. Frontend 실행
새 터미널 창에서:
```bash
cd frontend
# Python 내장 서버 사용
python -m http.server 5500

# 또는 Node.js가 설치되어 있다면
npx http-server -p 5500
```
브라우저에서 `http://localhost:5500` 접속

## 📚 API 문서

### API 문서 자동 생성
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 주요 엔드포인트

#### 환자 관련
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/patients` | 환자 목록 조회 (페이징) |
| GET | `/api/patients/search?query={keyword}` | 환자 검색 |
| GET | `/api/patients/{id}` | 환자 상세 정보 |
| POST | `/api/patients` | 신규 환자 등록 |
| GET | `/api/patients/stats/today` | 오늘의 통계 |

#### 진료 관련
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/visits` | 진료 기록 조회 |
| GET | `/api/visits/today` | 오늘의 진료 |
| POST | `/api/visits` | 진료 기록 추가 |
| GET | `/api/visits/departments` | 진료과 목록 |

#### 예약 관련
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/appointments` | 예약 목록 |
| GET | `/api/appointments/today` | 오늘의 예약 |
| GET | `/api/appointments/upcoming` | 향후 예약 |
| POST | `/api/appointments` | 예약 생성 |

## 💾 데이터베이스 구조

### ERD (Entity Relationship Diagram)
```
patients (환자)
    ├── patient_id (PK)
    ├── patient_no (UNIQUE)
    ├── name
    ├── birth_date
    ├── gender
    ├── phone
    └── created_at
         │
         ├──1:N──> visits (진료)
         │           ├── visit_id (PK)
         │           ├── patient_id (FK)
         │           ├── visit_date
         │           ├── department
         │           ├── doctor_name
         │           ├── diagnosis
         │           ├── status
         │           └── created_at
         │
         └──1:N──> appointments (예약)
                     ├── appointment_id (PK)
                     ├── patient_id (FK)
                     ├── appointment_date
                     ├── department
                     ├── doctor_name
                     ├── status
                     └── created_at
```

## 📁 프로젝트 구조

```
hospital-patient-system/
│
├── backend/
│   ├── main.py              # FastAPI 메인 서버
│   ├── database.py          # DB 연결 관리
│   ├── schemas.py           # Pydantic 모델
│   ├── requirements.txt     # Python 의존성
│   ├── upload_csv_to_api.py # 샘플 데이터 업로드
│   ├── .env                 # 환경변수 (생성 필요)
│   │
│   ├── routes/              # API 라우터
│   │   ├── __init__.py
│   │   ├── patients.py      # 환자 관련 엔드포인트
│   │   ├── visits.py        # 진료 관련 엔드포인트
│   │   └── appointments.py  # 예약 관련 엔드포인트
│   │
│   └── data/                # 샘플 데이터
│       ├── patients.csv     # 환자 샘플 데이터
│       ├── visits.csv       # 진료 샘플 데이터
│       ├── appointments.csv # 예약 샘플 데이터
│       └── departments.csv  # 진료과 데이터
│
├── frontend/
│   ├── index.html           # 메인 HTML
│   ├── hospital-style.css   # 스타일시트
│   └── hospital-app.js      # JavaScript 앱
│
├── README.md                # 프로젝트 문서
└── .gitignore              # Git 제외 파일
```

## 📸 스크린샷

### 로그인 화면
![로그인](./screenshots/login.png)

### 메인 대시보드
![대시보드](./screenshots/dashboard.png)

### 환자 검색
![환자검색](./screenshots/patient-search.png)

### 환자 상세 정보
![환자상세](./screenshots/patient-detail.png)

## 🔧 개발 가이드

### 코드 스타일
- **Python**: PEP 8 준수
- **JavaScript**: ES6+ 문법 사용
- **CSS**: BEM 명명 규칙

### 브랜치 전략
```
main (production)
  ├── develop
  │     ├── feature/patient-management
  │     ├── feature/appointment-system
  │     └── bugfix/api-error
  └── hotfix/critical-bug
```

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드 업무 수정
```

## 🧪 테스트

### API 테스트
```bash
# 헬스 체크
curl http://localhost:8000/health

# 환자 검색
curl "http://localhost:8000/api/patients/search?query=김"

# 오늘의 통계
curl http://localhost:8000/api/patients/stats/today
```

### 프론트엔드 테스트
1. 브라우저 개발자 도구 콘솔에서 에러 확인
2. 네트워크 탭에서 API 호출 확인
3. 반응형 디자인 테스트

## 🆘 문제 해결

### 일반적인 문제

#### 1. MySQL 연결 오류
```
Error: Can't connect to MySQL server
```
**해결방법:**
- MySQL 서비스가 실행 중인지 확인
- `.env` 파일의 데이터베이스 설정 확인
- 방화벽 설정 확인

#### 2. CORS 오류
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5500' has been blocked by CORS policy
```
**해결방법:**
- FastAPI의 CORS 미들웨어 설정 확인
- `main.py`의 `allow_origins` 설정 확인

#### 3. 포트 충돌
```
[Errno 48] Address already in use
```
**해결방법:**
```bash
# 사용 중인 포트 확인 (Mac/Linux)
lsof -i :8000

# 사용 중인 포트 확인 (Windows)
netstat -ano | findstr :8000

# 프로세스 종료 후 재시작
```

#### 4. 패키지 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements.txt
```

## 📝 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 기여 방법

1. 포크 생성 (`Fork`)
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📞 연락처

- **프로젝트 관리자**: admin@aixhospital.com
- **이슈 트래커**: [GitHub Issues](https://github.com/yourusername/hospital-patient-system/issues)
- **위키**: [GitHub Wiki](https://github.com/yourusername/hospital-patient-system/wiki)

## 🔄 업데이트 내역

### Version 1.0.0 (2024-12-24)
- 초기 릴리스
- 환자 관리 시스템 기본 기능 구현
- 대시보드, 환자 검색, 진료 기록, 예약 관리 기능

### 향후 계획
- [ ] 환자 사진 업로드 기능
- [ ] 진료 차트 시각화
- [ ] 처방전 발행 기능
- [ ] 보험 청구 연동
- [ ] 모바일 앱 개발
- [ ] 다국어 지원

---

**마지막 업데이트**: 2024년 12월 24일

**Made with ❤️ by AIX Hospital Development Team**
