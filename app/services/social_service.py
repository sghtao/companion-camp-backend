from app.services.twitter_client import TwitterClient


class SocialService:
    """
    소셜 미디어 서비스
    - X API를 통해 실제 사용자 데이터를 수집합니다.
    - 쓰기(Write)는 실제 TwitterClient API 사용
    """
    
    def __init__(self):
        self.twitter_client = TwitterClient()
    
    async def get_user_data(self, username: str) -> dict:
        """
        사용자 데이터 조회 (실제 X API 사용)
        
        Args:
            username: X(Twitter) 사용자명 (앳 기호 없이)
        
        Returns:
            소셜 미디어 통계 데이터 딕셔너리
        """
        # 사용자명에서 @ 제거
        username = username.lstrip('@')
        
        if not self.twitter_client.client:
            raise ValueError("Twitter 클라이언트가 초기화되지 않았습니다.")
        
        # 1. 사용자 정보 조회
        user_info = await self.twitter_client.get_user_by_username(username)
        if not user_info:
            raise ValueError(f"사용자 @{username}를 찾을 수 없습니다.")
        
        followers = user_info.get("followers_count", 0)
        
        # 2. 최근 트윗 조회 (최대 20개)
        user_id = str(user_info["id"])  # 문자열로 변환
        tweets = await self.twitter_client.get_user_tweets(user_id, max_results=20)
        
        if not tweets:
            # 트윗이 없는 경우 기본값 반환
            return {
                "username": username,
                "followers": followers,
                "avg_likes": 0,
                "avg_retweets": 0,
                "avg_replies": 0,
                "engagement_rate": 0.0,
                "reach_score": 0.0,
                "has_promotion_content": False,
                "has_banner_image": False
            }
        
        # 3. 평균 통계 계산
        total_likes = sum(tweet.get("like_count", 0) for tweet in tweets)
        total_retweets = sum(tweet.get("retweet_count", 0) for tweet in tweets)
        total_replies = sum(tweet.get("reply_count", 0) for tweet in tweets)
        
        avg_likes = total_likes // len(tweets) if tweets else 0
        avg_retweets = total_retweets // len(tweets) if tweets else 0
        avg_replies = total_replies // len(tweets) if tweets else 0
        
        # 4. 참여율 계산 (Engagement Rate)
        # 참여율 = (좋아요 + 리트윗 + 댓글) / 팔로워 수 * 100
        total_engagement = total_likes + total_retweets + total_replies
        avg_engagement_per_tweet = total_engagement / len(tweets) if tweets else 0
        engagement_rate = (avg_engagement_per_tweet / followers * 100) if followers > 0 else 0.0
        
        # 5. 콘텐츠 파급력 점수 계산 (0-10)
        # 참여율과 팔로워 수를 종합하여 점수 산정
        base_score = min(10.0, engagement_rate / 1.5)
        follower_bonus = min(2.0, followers / 50000)  # 팔로워 5만명당 2점 보너스
        reach_score = min(10.0, base_score + follower_bonus)
        
        # 6. 홍보 문구 및 배너 이미지 포함 여부 확인
        # 트윗 텍스트에서 홍보 관련 키워드 검색
        promotion_keywords = ["광고", "홍보", "협찬", "제공", "sponsored", "ad", "promotion"]
        has_promotion_content = any(
            any(keyword.lower() in tweet.get("text", "").lower() for keyword in promotion_keywords)
            for tweet in tweets
        )
        
        # 배너 이미지는 트윗에 미디어가 있는지로 판단 (현재는 간단히 False)
        # 실제로는 tweet_fields에 "attachments"를 추가하여 확인 가능
        has_banner_image = False
        
        return {
            "username": username,
            "followers": followers,
            "avg_likes": avg_likes,
            "avg_retweets": avg_retweets,
            "avg_replies": avg_replies,
            "engagement_rate": round(engagement_rate, 2),
            "reach_score": round(reach_score, 2),
            "has_promotion_content": has_promotion_content,
            "has_banner_image": has_banner_image
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

