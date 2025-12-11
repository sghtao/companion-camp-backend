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

    async def evaluate_content_quality(self, username: str, stats: dict, tweets: list) -> dict:
        """
        게시물의 품질을 평가하여 정성 점수를 산정합니다.
        - 오직 quality_score (0~100점 정수)만 반환합니다.
        
        Args:
            username: 펫 계정의 X(Twitter) 사용자명
            stats: 소셜 미디어 통계 데이터 (팔로워 수, 참여율, 콘텐츠 파급력 등)
            tweets: 최근 트윗 목록
        
        Returns:
            {
                "quality_score": 0~100 사이의 정수
            }
        """
        # 트윗 텍스트들을 하나의 문자열로 합치기 (최근 5개만)
        recent_tweets_text = "\n".join([
            tweet.get("text", "") for tweet in tweets[:5]
        ])
        
        # 프롬프트 작성
        prompt = f"""
당신은 펫 인플루언서 콘텐츠의 품질을 평가하는 전문가입니다.
다음 펫 계정의 콘텐츠를 분석하여 품질 점수를 산정해주세요.

**계정 정보:**
- 사용자명: @{username}
- 팔로워 수: {stats.get('followers', 0):,}명
- 평균 좋아요 수: {stats.get('avg_likes', 0):,}개
- 평균 리트윗 수: {stats.get('avg_retweets', 0):,}개
- 평균 댓글 수: {stats.get('avg_replies', 0):,}개
- 참여율 (Engagement Rate): {stats.get('engagement_rate', 0):.2f}%

**최근 게시물 내용:**
{recent_tweets_text[:1000] if recent_tweets_text else "게시물 없음"}

**평가 기준:**
1. **콘텐츠 품질**: 내용의 창의성, 유용성, 독창성
2. **작성 품질**: 문장의 명확성, 길이 적절성, 가독성
3. **참여 유도**: 팬덤과의 상호작용을 유도하는 정도
4. **일관성**: 브랜드 아이덴티티와의 일관성

**요구사항:**
- JSON 형식으로만 응답해주세요.
- quality_score만 포함해주세요 (0~100 사이의 정수).
- 보상 금액 계산은 하지 마세요. 오직 품질 점수만 제공하세요.

다음 JSON 형식으로 응답해주세요:
{{
    "quality_score": 0~100 사이의 정수
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
            quality_score = int(result.get("quality_score", 85))
            
            # 점수 범위 검증 (0~100)
            quality_score = max(0, min(100, quality_score))
            
            return {
                "quality_score": quality_score
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 에러: {e}")
            print(f"응답 내용: {response_text if 'response_text' in locals() else 'N/A'}")
            # 데모용 Mock 데이터 반환
            print("⚠️  Mock 데이터 반환: quality_score=85")
            return {"quality_score": 85}
            
        except Exception as e:
            # API 제한(429), 타임아웃 등 모든 예외에 대해 Mock 데이터 반환
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "timeout" in error_msg.lower():
                print(f"⚠️  API 제한/타임아웃 감지: {error_msg}")
            else:
                print(f"❌ AI 평가 에러: {error_msg}")
            
            # 데모가 멈추지 않도록 무조건 성공 데이터 반환
            print("⚠️  Mock 데이터 반환: quality_score=85")
            return {"quality_score": 85}

