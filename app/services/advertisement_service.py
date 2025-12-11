from typing import List, Dict
from app.services.social_service import SocialService


class AdvertisementService:
    """
    광고 서비스
    - 사용자 채널 볼륨에 맞춰 광고 단가 측정 및 맞춤 광고 추천
    """
    
    def __init__(self):
        self.social_service = SocialService()
    
    def calculate_ad_pricing(self, followers: int, engagement_rate: float) -> Dict[str, float]:
        """
        채널 볼륨에 맞춰 광고 단가 계산
        
        Args:
            followers: 팔로워 수
            engagement_rate: 참여율 (%)
        
        Returns:
            {
                "base_price": 기본 단가,
                "engagement_bonus": 참여율 보너스,
                "total_price": 총 단가
            }
        """
        # 기본 단가: 팔로워 1,000명당 1 토큰
        base_price = followers / 1000.0
        
        # 참여율 보너스: 참여율 1%당 10% 보너스
        engagement_bonus_rate = min(2.0, engagement_rate / 10.0)  # 최대 2배
        engagement_bonus = base_price * engagement_bonus_rate
        
        total_price = base_price + engagement_bonus
        
        return {
            "base_price": round(base_price, 2),
            "engagement_bonus": round(engagement_bonus, 2),
            "total_price": round(total_price, 2)
        }
    
    def get_recommended_advertisements(self, username: str, channel_volume: Dict) -> List[Dict]:
        """
        사용자에게 맞춤 광고 목록 제공
        - 채널 볼륨에 맞는 광고를 추천합니다.
        
        Args:
            username: 사용자명
            channel_volume: 채널 볼륨 정보 (followers, engagement_rate 등)
        
        Returns:
            맞춤 광고 목록
        """
        followers = channel_volume.get("followers", 0)
        engagement_rate = channel_volume.get("engagement_rate", 0.0)
        
        # 광고 단가 계산
        pricing = self.calculate_ad_pricing(followers, engagement_rate)
        
        # Mock 광고 데이터 (실제로는 DB에서 가져옴)
        mock_advertisements = [
            {
                "ad_id": "ad_001",
                "title": "프리미엄 펫 사료 프로모션",
                "ad_text": "🐾 최고급 펫 사료를 특가로 만나보세요! 지금 구매하면 20% 할인 + 무료배송! #펫사료 #반려동물",
                "banner_image_url": "https://example.com/banners/pet_food_banner.jpg",
                "pricing": pricing["total_price"],
                "category": "펫 케어",
                "suitable_for": "소형~중형 채널"
            },
            {
                "ad_id": "ad_002",
                "title": "반려동물 의류 신상품",
                "ad_text": "✨ 귀여운 반려동물 의류 신상품 출시! 따뜻한 겨울을 위한 필수 아이템 🧥 #펫패션 #반려동물의류",
                "banner_image_url": "https://example.com/banners/pet_clothing_banner.jpg",
                "pricing": pricing["total_price"],
                "category": "펫 패션",
                "suitable_for": "소형~중형 채널"
            },
            {
                "ad_id": "ad_003",
                "title": "펫 호텔 예약 서비스",
                "ad_text": "🏨 여행 가실 때 걱정 없이! 프리미엄 펫 호텔에서 반려동물을 안전하게 돌봐드립니다. 지금 예약하세요! #펫호텔 #펫케어",
                "banner_image_url": "https://example.com/banners/pet_hotel_banner.jpg",
                "pricing": pricing["total_price"],
                "category": "펫 서비스",
                "suitable_for": "중형~대형 채널"
            },
            {
                "ad_id": "ad_004",
                "title": "반려동물 건강검진 이벤트",
                "ad_text": "🏥 반려동물 건강검진 특가 이벤트! 정기 검진으로 건강한 반려생활을 시작하세요 💚 #펫건강 #반려동물검진",
                "banner_image_url": "https://example.com/banners/pet_checkup_banner.jpg",
                "pricing": pricing["total_price"],
                "category": "펫 케어",
                "suitable_for": "모든 채널"
            },
            {
                "ad_id": "ad_005",
                "title": "펫 용품 할인 이벤트",
                "ad_text": "🛍️ 반려동물 필수 용품 대할인! 장난감, 산책용품, 급여기 등 다양한 상품을 특가로! #펫용품 #반려동물용품",
                "banner_image_url": "https://example.com/banners/pet_supplies_banner.jpg",
                "pricing": pricing["total_price"],
                "category": "펫 용품",
                "suitable_for": "소형 채널"
            }
        ]
        
        # 채널 볼륨에 맞는 광고 필터링
        # 팔로워 수에 따라 적합한 광고 추천
        if followers < 5000:
            # 소형 채널: 모든 광고 추천
            recommended = mock_advertisements
        elif followers < 20000:
            # 중형 채널: 중형 이상 광고 추천
            recommended = [ad for ad in mock_advertisements if "소형" not in ad["suitable_for"]]
        else:
            # 대형 채널: 대형 채널용 광고만 추천
            recommended = [ad for ad in mock_advertisements if "대형" in ad["suitable_for"]]
        
        # 최소 3개는 추천
        if len(recommended) < 3:
            recommended = mock_advertisements[:3]
        
        return recommended
    
    async def get_user_channel_volume(self, username: str) -> Dict:
        """
        사용자 채널 볼륨 정보 조회
        
        Args:
            username: 사용자명
        
        Returns:
            채널 볼륨 정보 (팔로워, 참여율 등)
        """
        stats = await self.social_service.get_user_data(username)
        
        return {
            "username": username,
            "followers": stats.get("followers", 0),
            "engagement_rate": stats.get("engagement_rate", 0.0),
            "avg_likes": stats.get("avg_likes", 0),
            "avg_retweets": stats.get("avg_retweets", 0),
            "reach_score": stats.get("reach_score", 0.0)
        }

