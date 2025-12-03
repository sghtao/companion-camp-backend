from fastapi import FastAPI
from app.api import evaluation

app = FastAPI(
    title="Companion Camp Backend",
    description="펫 IP 플랫폼 백엔드 API",
    version="1.0.0"
)

# 라우터 등록
app.include_router(evaluation.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Companion Camp Backend API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

