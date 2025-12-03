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