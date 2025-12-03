import random
from app.services.twitter_client import TwitterClient


class SocialService:
    """
    소셜 미디어 서비스
    - X API Free Tier 한계로 인해 읽기(Read)는 Mock 데이터 사용
    - 쓰기(Write)는 실제 TwitterClient API 사용
    """
    
    def __init__(self):
        self.twitter_client = TwitterClient()
    
    async def get_user_data(self, username: str) -> dict:
        """
        사용자 데이터 조회 (Mock 데이터 반환)
        
        Args:
            username: X(Twitter) 사용자명
        
        Returns:
            소셜 미디어 통계 데이터 딕셔너리
        """
        # 랜덤한 Mock 데이터 생성
        # 실제 환경에서는 X API를 통해 데이터를 수집하지만,
        # Free Tier 제한으로 인해 Mock 데이터 사용
        
        base_followers = random.randint(1000, 100000)
        engagement_rate = random.uniform(1.0, 15.0)  # 1% ~ 15%
        
        # 참여율에 따라 좋아요, 리트윗, 댓글 수 계산
        avg_likes = int(base_followers * engagement_rate / 100 * random.uniform(0.3, 0.8))
        avg_retweets = int(avg_likes * random.uniform(0.1, 0.3))
        avg_replies = int(avg_likes * random.uniform(0.05, 0.2))
        
        # 콘텐츠 파급력 점수 (0-10)
        reach_score = min(10.0, engagement_rate / 1.5 + random.uniform(-1, 1))
        
        return {
            "username": username,
            "followers": base_followers,
            "avg_likes": avg_likes,
            "avg_retweets": avg_retweets,
            "avg_replies": avg_replies,
            "engagement_rate": round(engagement_rate, 2),
            "reach_score": round(reach_score, 2),
            "has_promotion_content": random.choice([True, False]),  # 홍보 문구 포함 여부
            "has_banner_image": random.choice([True, False])  # 배너 이미지 포함 여부
        }
    
    async def post_achievement(self, text: str) -> dict:
        """
        성과 공유 트윗 작성 (실제 API 사용)
        
        Args:
            text: 트윗 내용
        
        Returns:
            트윗 작성 결과
        """
        if not self.twitter_client.client:
            return {
                "status": "error",
                "message": "Twitter 클라이언트가 초기화되지 않았습니다."
            }
        
        try:
            result = await self.twitter_client.post_tweet(text)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"트윗 작성 실패: {str(e)}"
            }

