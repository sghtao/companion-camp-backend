from fastapi import APIRouter, Depends, Body
from app.services.advertisement_service import AdvertisementService
from app.services.social_service import SocialService
from typing import Optional, List, Dict

router = APIRouter(prefix="/advertisements", tags=["advertisements"])


# Dependency Injection을 위한 함수들
def get_advertisement_service() -> AdvertisementService:
    """AdvertisementService 인스턴스 생성 및 반환"""
    return AdvertisementService()


def get_social_service() -> SocialService:
    """SocialService 인스턴스 생성 및 반환"""
    return SocialService()


@router.get("/recommendations/{username}")
async def get_advertisement_recommendations(
    username: str,
    advertisement_service: AdvertisementService = Depends(get_advertisement_service)
):
    """
    사용자에게 맞춤 광고 목록 제공 API
    
    **기능:**
    1. 사용자 채널 볼륨 분석 (팔로워, 참여율 등)
    2. 채널 볼륨에 맞춰 광고 단가 계산
    3. 맞춤 광고 목록 제공 (텍스트 + 배너 이미지)
    
    Args:
        username: X(Twitter) 사용자명
    
    Returns:
        {
            "username": "사용자명",
            "channel_volume": {
                "followers": 팔로워 수,
                "engagement_rate": 참여율,
                ...
            },
            "pricing": {
                "base_price": 기본 단가,
                "engagement_bonus": 참여율 보너스,
                "total_price": 총 단가
            },
            "advertisements": [
                {
                    "ad_id": "광고 ID",
                    "title": "광고 제목",
                    "ad_text": "포스트에 추가할 텍스트",
                    "banner_image_url": "배너 이미지 URL",
                    "pricing": 단가,
                    "category": "카테고리",
                    "suitable_for": "적합한 채널 규모"
                },
                ...
            ]
        }
    """
    try:
        # 1. 사용자 채널 볼륨 조회
        channel_volume = await advertisement_service.get_user_channel_volume(username)
        
        # 2. 광고 단가 계산
        pricing = advertisement_service.calculate_ad_pricing(
            followers=channel_volume["followers"],
            engagement_rate=channel_volume["engagement_rate"]
        )
        
        # 3. 맞춤 광고 목록 제공
        advertisements = advertisement_service.get_recommended_advertisements(
            username=username,
            channel_volume=channel_volume
        )
        
        return {
            "username": username,
            "channel_volume": channel_volume,
            "pricing": pricing,
            "advertisements": advertisements
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "광고 추천 중 오류가 발생했습니다."
        }


@router.post("/select")
async def select_advertisement(
    username: str = Body(..., description="사용자명"),
    ad_id: str = Body(..., description="선택한 광고 ID"),
    wallet_address: str = Body(..., description="지갑 주소"),
    advertisement_service: AdvertisementService = Depends(get_advertisement_service)
):
    """
    사용자가 선택한 광고 저장 API
    
    **기능:**
    - 사용자가 선택한 광고 정보를 저장합니다.
    - 이후 게시물 평가 시 선택한 광고와 매칭하여 검증합니다.
    
    Args:
        username: 사용자명
        ad_id: 선택한 광고 ID
        wallet_address: 지갑 주소
    
    Returns:
        {
            "status": "success",
            "message": "광고 선택이 완료되었습니다.",
            "selected_ad": {
                "ad_id": "광고 ID",
                "username": "사용자명",
                "wallet_address": "지갑 주소",
                "selected_at": "선택 시간"
            }
        }
    """
    try:
        # 실제로는 DB에 저장하지만, 현재는 Mock으로 처리
        # TODO: 데이터베이스에 광고 선택 정보 저장
        
        from datetime import datetime
        
        selected_ad = {
            "ad_id": ad_id,
            "username": username,
            "wallet_address": wallet_address,
            "selected_at": datetime.now().isoformat()
        }
        
        print(f"📝 광고 선택 저장: {selected_ad}")
        
        return {
            "status": "success",
            "message": "광고 선택이 완료되었습니다.",
            "selected_ad": selected_ad
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "광고 선택 중 오류가 발생했습니다."
        }


@router.get("/selected/{username}")
async def get_selected_advertisement(
    username: str,
    advertisement_service: AdvertisementService = Depends(get_advertisement_service)
):
    """
    사용자가 선택한 광고 조회 API
    
    Args:
        username: 사용자명
    
    Returns:
        {
            "username": "사용자명",
            "selected_ad": {
                "ad_id": "광고 ID",
                "selected_at": "선택 시간",
                ...
            }
        }
    """
    try:
        # 실제로는 DB에서 조회하지만, 현재는 Mock으로 처리
        # TODO: 데이터베이스에서 광고 선택 정보 조회
        
        return {
            "username": username,
            "selected_ad": None,  # 현재는 Mock
            "message": "선택한 광고가 없습니다."
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "광고 조회 중 오류가 발생했습니다."
        }

