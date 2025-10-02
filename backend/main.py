from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# 라우터 import
from routes import patients, visits, appointments

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="병원 환자 조회 시스템 API",
    description="환자 정보, 진료 기록, 예약 관리를 위한 RESTful API",
    version="1.0.0"
)

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(patients.router)
app.include_router(visits.router)
app.include_router(appointments.router)

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "병원 환자 조회 시스템 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    from database import get_db_connection
    
    # DB 연결 테스트
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"status": "healthy", "database": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Database connection failed")

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"서버 오류가 발생했습니다: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 개발 중에는 자동 리로드 활성화
    )

    