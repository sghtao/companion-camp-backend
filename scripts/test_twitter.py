import asyncio
import sys
import os

# 현재 폴더 위치를 파이썬에게 알려줌 (app 폴더를 찾기 위해)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.twitter_client import TwitterClient

async def test():
    print("--- 🔄 X API 연동 테스트 시작 ---")
    
    # 1. 클라이언트 생성 (연결 시도)
    twitter = TwitterClient()
    
    # 2. 내 정보 조회 (인증 테스트)
    print("\n1️⃣ 내 계정 정보 조회 중...")
    me = await twitter.get_my_info()
    
    if me:
        print(f"✅ 성공! 연결된 계정: @{me['username']} (이름: {me['name']})")
        print("🎉 축하합니다! API 키가 완벽하게 작동합니다.")
    else:
        print("❌ 실패: .env 파일의 키 값을 다시 확인해주세요.")
        print("   (팁: Access Token 권한이 Read and Write인지 확인해보세요)")

if __name__ == "__main__":
    asyncio.run(test())