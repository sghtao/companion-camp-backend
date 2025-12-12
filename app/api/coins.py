"""
Coins API endpoints for meme coin market
Handles coin listing, purchase recording, and purchase history
"""
from fastapi import APIRouter, Depends, Body, HTTPException
from app.services.coin_service import CoinService
from app.db import insert_purchase, get_history_by_username
from typing import List, Dict
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/coins", tags=["coins"])


# Request/Response Models
class PurchaseRequest(BaseModel):
    """Request model for coin purchase"""
    username: str
    coin_symbol: str
    amount: float
    tx_hash: str


class PurchaseResponse(BaseModel):
    """Response model for coin purchase"""
    status: str
    saved_id: int
    message: str


# Dependency Injection
def get_coin_service() -> CoinService:
    """CoinService 인스턴스 생성 및 반환"""
    return CoinService()


@router.get("")
async def get_coins(
    coin_service: CoinService = Depends(get_coin_service)
) -> List[Dict]:
    """
    Get list of available meme coins with real-time prices from DexScreener
    
    **기능:**
    - DexScreener API를 통해 실시간 Solana 밈코인 가격 정보를 가져옵니다.
    - 각 코인의 이름, 심볼, 가격, 24시간 변동률 등을 반환합니다.
    
    Returns:
        List[Dict]: List of coin data with:
            - name: Coin name
            - symbol: Coin symbol (e.g., "BONK", "WIF")
            - priceUsd: Current price in USD
            - priceChange24h: 24-hour price change percentage
            - imageUrl: Coin logo URL
            - address: Solana contract address
            - volume24h: 24-hour trading volume
            - liquidity: Current liquidity in USD
    """
    try:
        coins = await coin_service.get_coin_list()
        return coins
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch coin data: {str(e)}"
        )


@router.post("/purchase")
async def purchase_coin(
    purchase: PurchaseRequest = Body(..., description="Purchase transaction data"),
) -> PurchaseResponse:
    """
    Record a coin purchase transaction
    
    **기능:**
    - 사용자의 밈코인 구매 트랜잭션을 데이터베이스에 저장합니다.
    - 트랜잭션 해시, 코인 심볼, 구매 금액 등을 기록합니다.
    
    **워크플로우:**
    1. 밈코인 구매 요청 (프론트엔드)
    2. 서명 (지갑)
    3. 컨트랙트에 트랜잭션 전송 -> 실행
    4. 거래 결과를 이 API로 전송하여 저장
    
    Args:
        purchase: Purchase transaction data containing:
            - username: Username of the purchaser
            - coin_symbol: Symbol of the coin (e.g., "BONK", "WIF")
            - amount: Amount of coins purchased
            - tx_hash: Transaction hash from blockchain
    
    Returns:
        PurchaseResponse: Success status and saved record ID
    """
    try:
        # Validate inputs
        if not purchase.username or not purchase.username.strip():
            raise HTTPException(status_code=400, detail="Username is required")
        
        if not purchase.coin_symbol or not purchase.coin_symbol.strip():
            raise HTTPException(status_code=400, detail="Coin symbol is required")
        
        if purchase.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        if purchase.amount > 1e15:  # Prevent unrealistic values
            raise HTTPException(status_code=400, detail="Amount too large")
        
        if not purchase.tx_hash or not purchase.tx_hash.strip():
            raise HTTPException(status_code=400, detail="Transaction hash is required")
        
        # Save to database
        try:
            saved_id = insert_purchase(
                username=purchase.username,
                coin_symbol=purchase.coin_symbol.upper(),
                amount=purchase.amount,
                tx_hash=purchase.tx_hash
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: Failed to save purchase. {str(e)}"
            )
        
        return PurchaseResponse(
            status="success",
            saved_id=saved_id,
            message="Purchase transaction saved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save purchase: {str(e)}"
        )


@router.get("/history/{username}")
async def get_purchase_history(username: str) -> Dict:
    """
    Get purchase history for a specific user
    
    **기능:**
    - 특정 사용자의 모든 밈코인 구매 내역을 조회합니다.
    - 최신 구매 내역부터 정렬하여 반환합니다.
    
    Args:
        username: Username to query purchase history for
    
    Returns:
        Dict: Purchase history containing:
            - username: Username
            - purchases: List of purchase records with:
                - id: Purchase record ID
                - coin_symbol: Coin symbol
                - amount: Amount purchased
                - tx_hash: Transaction hash
                - created_at: Purchase timestamp
    """
    try:
        if not username or not username.strip():
            raise HTTPException(status_code=400, detail="Username is required")
        
        purchases = get_history_by_username(username)
        
        return {
            "username": username,
            "purchases": purchases,
            "total_purchases": len(purchases)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch purchase history: {str(e)}"
        )

