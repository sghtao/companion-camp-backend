from fastapi import APIRouter, Depends, Body, HTTPException
from app.services.ai_service import AIService
from app.services.social_service import SocialService
from app.services.contract_service import ContractService
from typing import Optional

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


# Dependency Injection을 위한 함수들
def get_ai_service() -> AIService:
    """AIService 인스턴스 생성 및 반환"""
    return AIService()


def get_social_service() -> SocialService:
    """SocialService 인스턴스 생성 및 반환"""
    return SocialService()


def get_contract_service() -> ContractService:
    """ContractService 인스턴스 생성 및 반환"""
    return ContractService()


@router.post("/analyze/{username}")
async def analyze_pet_account(
    username: str,
    wallet_address: str = Body(..., description="보상을 받을 지갑 주소"),
    required_keyword: Optional[str] = Body(None, description="필수 광고 키워드 (선택사항)"),
    ai_service: AIService = Depends(get_ai_service),
    social_service: SocialService = Depends(get_social_service),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    펫 계정 분석 및 보상 지급 워크플로우 API
    
    **보상 지급 프로세스 1~6단계:**
    1. 데이터 수집: SocialService를 통해 사용자 정보와 게시물을 가져옵니다.
    2. 광고 검증: 게시물이 특정 광고 문구와 배너 이미지를 포함했는지 확인합니다.
    3. 정량 데이터 확인: 팔로워, 좋아요, 리포스트 등의 수치 데이터를 확보합니다.
    4. 정성 평가 (AI): Gemini를 통해 게시물의 품질을 점수화합니다.
    5. 최종 점수 산정 & 컨트랙트 전송: (정량 점수 + 정성 점수)로 Total Score를 계산하여 컨트랙트로 보냅니다.
    6. 결과 반환: 컨트랙트가 지급한 토큰 개수와 트랜잭션 해시를 반환합니다.
    
    Args:
        username: 분석할 펫 계정의 X(Twitter) 사용자명
        wallet_address: 보상을 받을 지갑 주소
        required_keyword: 필수 광고 키워드 (선택사항, 기본값: None)
        ai_service: AIService 의존성 주입
        social_service: SocialService 의존성 주입
        contract_service: ContractService 의존성 주입
    
    Returns:
        {
            "username": "사용자명",
            "verification": { "is_ad_verified": true },
            "scores": { "social_score": 00, "ai_score": 00, "final_score": 00 },
            "reward": { "tx_hash": "0x...", "amount": 500 }
        }
    """
    try:
        # ===== 1단계: 데이터 수집 =====
        print(f"\n📊 [1단계] 데이터 수집 시작: @{username}")
        stats = await social_service.get_user_data(username)
        tweets = await social_service.get_user_tweets(username, max_results=20)
        
        if not tweets:
            return {
                "error": "트윗 데이터가 없습니다.",
                "message": "분석할 게시물이 없습니다."
            }
        
        # ===== 2단계: 광고 검증 (Ad Verification) =====
        print(f"\n✅ [2단계] 광고 검증 시작")
        is_ad_verified = False
        has_banner = False
        
        if required_keyword:
            # 최근 트윗들에서 필수 키워드 검색
            for tweet in tweets[:5]:  # 최근 5개 트윗만 확인
                tweet_text = tweet.get("text", "")
                if social_service.verify_ad_compliance(tweet_text, required_keyword):
                    is_ad_verified = True
                    break
        else:
            # 키워드가 지정되지 않은 경우, 기본 홍보 키워드로 확인
            promotion_keywords = ["광고", "홍보", "협찬", "제공", "sponsored", "ad", "promotion"]
            for tweet in tweets[:5]:
                tweet_text = tweet.get("text", "")
                if any(social_service.verify_ad_compliance(tweet_text, keyword) for keyword in promotion_keywords):
                    is_ad_verified = True
                    break
        
        # 배너 이미지 검증 (Mock: 항상 True)
        has_banner = social_service.verify_banner_image()
        
        # 광고 검증 통과 여부 (키워드 또는 배너 중 하나라도 있으면 통과)
        is_ad_verified = is_ad_verified or has_banner
        
        # ===== 3단계: 정량 데이터 확인 =====
        print(f"\n📈 [3단계] 정량 데이터 확인")
        # stats None 체크 추가
        if not stats:
            stats = {}
        # stats에서 reach_score를 가져와서 100점 만점으로 변환
        social_reach_score = stats.get("reach_score", 0.0)  # 0~10 점수
        social_score = (social_reach_score / 10.0) * 100 if social_reach_score > 0 else 0.0  # 0~100 점수로 변환
        
        print(f"   - 팔로워 수: {stats.get('followers', 0):,}명")
        print(f"   - 참여율: {stats.get('engagement_rate', 0):.2f}%")
        print(f"   - 소셜 점수: {social_score:.2f}/100")
        
        # ===== 4단계: 정성 평가 (AI) =====
        print(f"\n🤖 [4단계] 정성 평가 (AI) 시작")
        ai_result = await ai_service.evaluate_content_quality(username, stats, tweets)
        ai_score = ai_result.get("quality_score", 85)
        identity_score = ai_result.get("identity_score", 0)
        fandom_score = ai_result.get("fandom_score", 0)
        safety_score = ai_result.get("safety_score", 0)
        analysis_summary = ai_result.get("analysis_summary", "분석 결과 없음")
        
        print(f"   - AI 품질 점수: {ai_score}/100")
        print(f"   - Identity 점수: {identity_score}/40")
        print(f"   - Fandom 점수: {fandom_score}/30")
        print(f"   - Safety 점수: {safety_score}/30")
        
        # ===== 5단계: 최종 점수 산정 & 컨트랙트 전송 =====
        print(f"\n💰 [5단계] 최종 점수 산정 & 컨트랙트 전송")
        # 점수 산식: Final Score = (Social Reach Score * 40) + (AI Quality Score * 60)
        final_score = int((social_score * 0.4) + (ai_score * 0.6))
        final_score = max(0, min(100, final_score))  # 0~100 범위 보장
        
        print(f"   - 최종 점수: {final_score}/100")
        print(f"   - 계산식: ({social_score:.2f} * 0.4) + ({ai_score} * 0.6) = {final_score}")
        
        # 컨트랙트에 트랜잭션 전송 (에러 처리 추가)
        try:
            reward_result = await contract_service.execute_reward_transaction(
                wallet_address=wallet_address,
                score=final_score
            )
        except Exception as e:
            print(f"⚠️  Contract service failed: {e}")
            # Fallback to safe defaults
            reward_result = {
                "tx_hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "rewarded_amount": 0
            }
        
        # ===== 6단계: 결과 반환 =====
        print(f"\n✅ [6단계] 결과 반환 완료")
        
        return {
            "username": username,
            "verification": {
                "is_ad_verified": is_ad_verified,
                "has_banner": has_banner
            },
            "scores": {
                "social_score": round(social_score, 2),
                "ai_score": ai_score,
                "final_score": final_score,
                "details": {
                    "identity": identity_score,
                    "fandom": fandom_score,
                    "safety": safety_score
                }
            },
            "analysis_summary": analysis_summary,
            "reward": {
                "tx_hash": reward_result.get("tx_hash") or "N/A",
                "amount": reward_result.get("rewarded_amount") or 0,
                "wallet_address": wallet_address
            }
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()  # Better debugging
        raise HTTPException(
            status_code=500,
            detail=f"펫 계정 분석 중 오류가 발생했습니다: {str(e)}"
        )

