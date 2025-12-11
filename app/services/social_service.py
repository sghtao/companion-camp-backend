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
        사용자 데이터 조회 (Mock 모드 - 데모용)
        - X API 무료 플랜 제한(429 Error)으로 인해 Mock 데이터를 반환합니다.
        - 실제 API 호출 코드는 주석 처리되어 있습니다.
        
        Args:
            username: X(Twitter) 사용자명 (앳 기호 없이)
        
        Returns:
            소셜 미디어 통계 데이터 딕셔너리 (Mock 데이터)
        """
        # 사용자명에서 @ 제거
        username = username.lstrip('@')
        
        # ===== Mock 모드: API 호출 없이 즉시 반환 =====
        # 데모 시연을 위해 어떤 아이디를 넣어도 항상 성공하는 Mock 데이터 반환
        print(f"📊 [Mock] 사용자 데이터 조회: @{username} (Mock 데이터 반환)")
        
        return {
            "username": username,
            "followers": 15200,          # 1.5만 명 (데모용)
            "avg_likes": 350,            # 좋아요 수
            "avg_retweets": 45,          # 리트윗 수
            "avg_replies": 12,
            "engagement_rate": 4.5,      # 참여율 (높게 설정)
            "reach_score": 8.5,          # 파급력 점수 (10점 만점)
            "has_promotion_content": True, # 광고 문구 포함 (Pass)
            "has_banner_image": True       # 배너 이미지 포함 (Pass)
        }
        
        # ===== 실제 API 호출 코드 (주석 처리) =====
        # X API 제한으로 인해 현재 사용하지 않음
        # """
        # if not self.twitter_client.client:
        #     raise ValueError("Twitter 클라이언트가 초기화되지 않았습니다.")
        # 
        # # 1. 사용자 정보 조회
        # user_info = await self.twitter_client.get_user_by_username(username)
        # if not user_info:
        #     raise ValueError(f"사용자 @{username}를 찾을 수 없습니다.")
        # 
        # followers = user_info.get("followers_count", 0)
        # 
        # # 2. 최근 트윗 조회 (최대 20개)
        # user_id = str(user_info["id"])  # 문자열로 변환
        # tweets = await self.twitter_client.get_user_tweets(user_id, max_results=20)
        # 
        # if not tweets:
        #     # 트윗이 없는 경우 기본값 반환
        #     return {
        #         "username": username,
        #         "followers": followers,
        #         "avg_likes": 0,
        #         "avg_retweets": 0,
        #         "avg_replies": 0,
        #         "engagement_rate": 0.0,
        #         "reach_score": 0.0,
        #         "has_promotion_content": False,
        #         "has_banner_image": False
        #     }
        # 
        # # 3. 평균 통계 계산
        # total_likes = sum(tweet.get("like_count", 0) for tweet in tweets)
        # total_retweets = sum(tweet.get("retweet_count", 0) for tweet in tweets)
        # total_replies = sum(tweet.get("reply_count", 0) for tweet in tweets)
        # 
        # avg_likes = total_likes // len(tweets) if tweets else 0
        # avg_retweets = total_retweets // len(tweets) if tweets else 0
        # avg_replies = total_replies // len(tweets) if tweets else 0
        # 
        # # 4. 참여율 계산 (Engagement Rate)
        # # 참여율 = (좋아요 + 리트윗 + 댓글) / 팔로워 수 * 100
        # total_engagement = total_likes + total_retweets + total_replies
        # avg_engagement_per_tweet = total_engagement / len(tweets) if tweets else 0
        # engagement_rate = (avg_engagement_per_tweet / followers * 100) if followers > 0 else 0.0
        # 
        # # 5. 콘텐츠 파급력 점수 계산 (0-10)
        # # 참여율과 팔로워 수를 종합하여 점수 산정
        # base_score = min(10.0, engagement_rate / 1.5)
        # follower_bonus = min(2.0, followers / 50000)  # 팔로워 5만명당 2점 보너스
        # reach_score = min(10.0, base_score + follower_bonus)
        # 
        # # 6. 홍보 문구 및 배너 이미지 포함 여부 확인
        # # 트윗 텍스트에서 홍보 관련 키워드 검색
        # promotion_keywords = ["광고", "홍보", "협찬", "제공", "sponsored", "ad", "promotion"]
        # has_promotion_content = any(
        #     any(keyword.lower() in tweet.get("text", "").lower() for keyword in promotion_keywords)
        #     for tweet in tweets
        # )
        # 
        # # 배너 이미지는 트윗에 미디어가 있는지로 판단 (현재는 간단히 False)
        # # 실제로는 tweet_fields에 "attachments"를 추가하여 확인 가능
        # has_banner_image = False
        # 
        # return {
        #     "username": username,
        #     "followers": followers,
        #     "avg_likes": avg_likes,
        #     "avg_retweets": avg_retweets,
        #     "avg_replies": avg_replies,
        #     "engagement_rate": round(engagement_rate, 2),
        #     "reach_score": round(reach_score, 2),
        #     "has_promotion_content": has_promotion_content,
        #     "has_banner_image": has_banner_image
        # }
        # """
    
    async def get_user_tweets(self, username: str, max_results: int = 20) -> list:
        """
        사용자의 최근 트윗 목록 조회 (Mock 모드 - 데모용)
        - X API 무료 플랜 제한(429 Error)으로 인해 Mock 데이터를 반환합니다.
        - 실제 API 호출 코드는 주석 처리되어 있습니다.
        
        Args:
            username: X(Twitter) 사용자명 (앳 기호 없이)
            max_results: 가져올 트윗 수 (최대 100)
        
        Returns:
            트윗 목록 리스트 (Mock 데이터)
        """
        username = username.lstrip('@')
        
        # ===== Mock 모드: API 호출 없이 즉시 반환 =====
        # 데모 시연을 위해 어떤 아이디를 넣어도 항상 성공하는 Mock 트윗 데이터 반환
        print(f"📝 [Mock] 트윗 목록 조회: @{username} (Mock 데이터 반환)")
        
        # Mock 트윗 데이터 생성 (광고 키워드 포함)
        mock_tweets = [
            {
                "id": f"mock_tweet_{i}",
                "text": f"오늘도 귀여운 {username}의 일상입니다! 🐾 #펫스타그램 #반려동물 #광고",
                "like_count": 350 + (i * 10),
                "retweet_count": 45 + (i * 2),
                "reply_count": 12 + i,
                "created_at": f"2024-01-{10+i:02d}T10:00:00Z"
            }
            for i in range(min(max_results, 5))  # 최대 5개 Mock 트윗 생성
        ]
        
        return mock_tweets
        
        # ===== 실제 API 호출 코드 (주석 처리) =====
        # X API 제한으로 인해 현재 사용하지 않음
        # """
        # if not self.twitter_client.client:
        #     raise ValueError("Twitter 클라이언트가 초기화되지 않았습니다.")
        # 
        # # 사용자 정보 조회
        # user_info = await self.twitter_client.get_user_by_username(username)
        # if not user_info:
        #     raise ValueError(f"사용자 @{username}를 찾을 수 없습니다.")
        # 
        # # 트윗 조회
        # user_id = str(user_info["id"])
        # tweets = await self.twitter_client.get_user_tweets(user_id, max_results=max_results)
        # 
        # return tweets
        # """
    
    def verify_ad_compliance(self, tweet_text: str, required_keyword: str) -> bool:
        """
        광고 문구 검증 메서드
        - 트윗 내용에 필수 키워드가 포함되어 있는지 확인합니다.
        
        Args:
            tweet_text: 트윗 텍스트 내용
            required_keyword: 필수로 포함되어야 하는 광고 키워드
        
        Returns:
            키워드 포함 여부 (Boolean)
        """
        if not tweet_text or not required_keyword:
            return False
        
        # 대소문자 구분 없이 검색
        return required_keyword.lower() in tweet_text.lower()
    
    def verify_banner_image(self) -> bool:
        """
        배너 이미지 검증 메서드 (Mock)
        - 데모용으로 항상 True를 반환합니다.
        - 실제 구현 시에는 트윗의 미디어 첨부 여부를 확인합니다.
        
        Returns:
            배너 이미지 포함 여부 (항상 True)
        """
        # 데모용 Mock 로직: 항상 True 반환
        return True
    
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

