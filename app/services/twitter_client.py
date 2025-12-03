import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

class TwitterClient:
    def __init__(self):
        # 1. 환경변수(.env)에서 키 가져오기
        self.api_key = os.getenv("X_API_KEY")
        self.api_secret = os.getenv("X_API_SECRET")
        self.access_token = os.getenv("X_ACCESS_TOKEN")
        self.access_secret = os.getenv("X_ACCESS_SECRET")
        self.bearer_token = os.getenv("X_BEARER_TOKEN")

        # 2. X API v2 클라이언트 연결 (Free Plan용)
        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )
            print("🐦 X(Twitter) Client 연결 시도...")
        except Exception as e:
            print(f"❌ X 연결 실패: {e}")
            self.client = None

    async def get_my_info(self):
        """
        [테스트용] 내 계정 정보 확인
        - API 키가 맞는지 확인하는 용도입니다.
        """
        if not self.client:
            return None
            
        try:
            # 내 정보(아이디, 이름, 프로필사진) 가져오기
            response = self.client.get_me(user_fields=["profile_image_url"])
            if response.data:
                user = response.data
                return {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name
                }
            return None
        except Exception as e:
            print(f"❌ 내 정보 조회 에러: {e}")
            return None

    async def get_user_by_username(self, username: str):
        """
        사용자명으로 사용자 정보 조회
        
        Args:
            username: X(Twitter) 사용자명 (앳 기호 없이)
        
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        if not self.client:
            return None
        
        try:
            # 사용자명으로 사용자 정보 가져오기
            response = self.client.get_user(
                username=username,
                user_fields=["public_metrics", "description", "profile_image_url"]
            )
            if response.data:
                user = response.data
                metrics = user.public_metrics if hasattr(user, 'public_metrics') else {}
                return {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "followers_count": metrics.get("followers_count", 0) if metrics else 0,
                    "following_count": metrics.get("following_count", 0) if metrics else 0,
                    "tweet_count": metrics.get("tweet_count", 0) if metrics else 0,
                    "description": user.description if hasattr(user, 'description') else ""
                }
            return None
        except Exception as e:
            print(f"❌ 사용자 정보 조회 에러: {e}")
            return None

    async def get_user_tweets(self, user_id: str, max_results: int = 10):
        """
        사용자의 최근 트윗 목록 조회
        
        Args:
            user_id: 사용자 ID
            max_results: 가져올 트윗 수 (최대 100)
        
        Returns:
            트윗 목록 리스트
        """
        if not self.client:
            return []
        
        try:
            tweets = []
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=["public_metrics", "created_at", "text"]
            )
            
            if response.data:
                for tweet in response.data:
                    metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "like_count": metrics.get("like_count", 0) if metrics else 0,
                        "retweet_count": metrics.get("retweet_count", 0) if metrics else 0,
                        "reply_count": metrics.get("reply_count", 0) if metrics else 0,
                        "created_at": str(tweet.created_at) if hasattr(tweet, 'created_at') else None
                    })
            
            return tweets
        except Exception as e:
            print(f"❌ 트윗 조회 에러: {e}")
            return []

    async def post_tweet(self, text: str):
        """
        [핵심 기능] 트윗 쓰기
        - 보상 받은 걸 자랑할 때 씁니다.
        """
        try:
            response = self.client.create_tweet(text=text)
            return {"status": "success", "id": response.data['id']}
        except Exception as e:
            return {"status": "error", "message": str(e)}