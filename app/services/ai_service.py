import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()


class AIService:
    def __init__(self):
        """
        AI 서비스 초기화
        - Gemini Pro 모델을 사용하여 펫 IP 가치 평가를 수행합니다.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("❌ 오류: .env 파일에 GEMINI_API_KEY가 없습니다!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")
        print("🤖 AIService 초기화 완료")

    async def evaluate_pet_value(self, username: str, stats: dict) -> dict:
        """
        펫 계정의 가치를 평가하여 등급과 보상 금액을 산정합니다.
        
        Args:
            username: 펫 계정의 X(Twitter) 사용자명
            stats: 소셜 미디어 통계 데이터 (팔로워 수, 참여율, 콘텐츠 파급력 등)
        
        Returns:
            {
                "grade": "등급 (예: S, A, B, C)",
                "reward_amount": 보상 금액 (숫자),
                "evaluation_reason": "평가 근거 설명"
            }
        """
        # 프롬프트 작성
        prompt = f"""
당신은 펫 인플루언서 IP의 가치를 평가하는 전문가입니다. 
다음 펫 계정의 소셜 미디어 활동 데이터를 분석하여 공정하고 투명한 가치 평가를 수행해주세요.

**계정 정보:**
- 사용자명: @{username}
- 팔로워 수: {stats.get('followers', 0):,}명
- 평균 좋아요 수: {stats.get('avg_likes', 0):,}개
- 평균 리트윗 수: {stats.get('avg_retweets', 0):,}개
- 평균 댓글 수: {stats.get('avg_replies', 0):,}개
- 참여율 (Engagement Rate): {stats.get('engagement_rate', 0):.2f}%
- 콘텐츠 파급력 점수: {stats.get('reach_score', 0):.2f}/10

**평가 기준:**
1. **콘텐츠 파급력**: 팔로워 수, 리치(Reach), 바이럴 확산 정도
2. **팬덤 참여율**: 좋아요, 리트윗, 댓글 등 상호작용 지표
3. **브랜드 가치**: 일관성 있는 콘텐츠, 고유한 매력, 커뮤니티 형성
4. **광고 적합성**: 홍보 문구 및 배너 포함 여부, 자연스러운 통합

**등급 체계:**
- S등급: 최상위 인플루언서 (보상: 10,000-50,000 토큰)
- A등급: 우수한 인플루언서 (보상: 5,000-10,000 토큰)
- B등급: 중상위 인플루언서 (보상: 1,000-5,000 토큰)
- C등급: 일반 인플루언서 (보상: 100-1,000 토큰)

**요구사항:**
- JSON 형식으로만 응답해주세요.
- 등급(grade), 보상금액(reward_amount), 평가근거(evaluation_reason)를 포함해주세요.
- 보상금액은 토큰 단위의 정수로 제공해주세요.

다음 JSON 형식으로 응답해주세요:
{{
    "grade": "등급",
    "reward_amount": 숫자,
    "evaluation_reason": "상세한 평가 근거 설명"
}}
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON 파싱 시도 (마크다운 코드 블록 제거)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            return {
                "grade": result.get("grade", "C"),
                "reward_amount": int(result.get("reward_amount", 100)),
                "evaluation_reason": result.get("evaluation_reason", "기본 평가")
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 에러: {e}")
            print(f"응답 내용: {response_text}")
            # 기본값 반환
            return {
                "grade": "C",
                "reward_amount": 100,
                "evaluation_reason": "AI 평가 중 오류 발생"
            }
        except Exception as e:
            print(f"❌ AI 평가 에러: {e}")
            return {
                "grade": "C",
                "reward_amount": 100,
                "evaluation_reason": f"평가 중 오류 발생: {str(e)}"
            }

