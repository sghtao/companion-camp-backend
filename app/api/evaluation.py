from fastapi import APIRouter, Depends
from app.services.ai_service import AIService
from app.services.social_service import SocialService

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


# Dependency Injection을 위한 함수들
def get_ai_service() -> AIService:
    """AIService 인스턴스 생성 및 반환"""
    return AIService()


def get_social_service() -> SocialService:
    """SocialService 인스턴스 생성 및 반환"""
    return SocialService()


@router.post("/analyze/{username}")
async def analyze_pet_account(
    username: str,
    ai_service: AIService = Depends(get_ai_service),
    social_service: SocialService = Depends(get_social_service)
):
    """
    펫 계정 분석 및 가치 평가 API
    
    - SocialService로 소셜 미디어 데이터 수집
    - AIService로 가치 평가 수행
    - 등급 및 보상 금액 반환
    
    Args:
        username: 분석할 펫 계정의 X(Twitter) 사용자명
        ai_service: AIService 의존성 주입
        social_service: SocialService 의존성 주입
    
    Returns:
        {
            "username": "계정명",
            "stats": {...소셜 미디어 통계...},
            "evaluation": {
                "grade": "등급",
                "reward_amount": 보상금액,
                "evaluation_reason": "평가 근거"
            }
        }
    """
    try:
        # 1. 소셜 미디어 데이터 수집
        stats = await social_service.get_user_data(username)
        
        # 2. AI를 통한 가치 평가
        evaluation = await ai_service.evaluate_pet_value(username, stats)
        
        return {
            "username": username,
            "stats": stats,
            "evaluation": evaluation
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "펫 계정 분석 중 오류가 발생했습니다."
        }

