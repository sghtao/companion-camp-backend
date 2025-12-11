import hashlib
import random
from typing import Dict


class ContractService:
    """
    스마트 컨트랙트 서비스
    - 블록체인과의 통신을 담당합니다.
    - 현재는 Mock 구현으로 시뮬레이션합니다.
    """
    
    def __init__(self):
        """ContractService 초기화"""
        print("📝 ContractService 초기화 완료 (Mock 모드)")
    
    async def execute_reward_transaction(self, wallet_address: str, score: int) -> Dict[str, any]:
        """
        보상 트랜잭션 실행 (Mock)
        - 입력받은 score에 따라 토큰 양을 계산하고 가짜 tx_hash를 반환합니다.
        
        Args:
            wallet_address: 보상을 받을 지갑 주소
            score: 최종 점수 (0~100)
        
        Returns:
            {
                "tx_hash": "가짜 트랜잭션 해시",
                "rewarded_amount": 계산된 토큰 양,
                "wallet_address": 지갑 주소
            }
        """
        # 점수에 따른 토큰 양 계산 (예: score * 10)
        # 최소 100 토큰, 최대 10,000 토큰
        rewarded_amount = max(100, min(10000, score * 10))
        
        # 가짜 트랜잭션 해시 생성 (데모용)
        # 실제로는 블록체인에 트랜잭션을 전송하고 반환된 해시를 사용합니다.
        hash_input = f"{wallet_address}_{score}_{random.randint(1000, 9999)}"
        fake_tx_hash = "0x" + hashlib.sha256(hash_input.encode()).hexdigest()[:64]
        
        print(f"💰 보상 트랜잭션 시뮬레이션:")
        print(f"   - 지갑 주소: {wallet_address}")
        print(f"   - 점수: {score}")
        print(f"   - 보상 금액: {rewarded_amount} 토큰")
        print(f"   - 트랜잭션 해시: {fake_tx_hash}")
        
        return {
            "tx_hash": fake_tx_hash,
            "rewarded_amount": rewarded_amount,
            "wallet_address": wallet_address
        }

