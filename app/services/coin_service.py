"""
Coin Service for fetching real-time Solana meme coin prices from DexScreener API
"""
import aiohttp
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Popular Solana Meme Coin Contract Addresses
# These are the actual Solana token contract addresses for meme coins
SOLANA_MEME_COINS = {
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK on Solana
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",  # dogwifhat (WIF) on Solana
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT on Solana
}


class CoinService:
    """Service for fetching real-time coin market data from DexScreener"""
    
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex/tokens"
        self.coin_addresses = list(SOLANA_MEME_COINS.values())
    
    async def get_coin_list(self) -> List[Dict]:
        """
        Fetch real-time prices for Solana meme coins from DexScreener API
        
        Returns:
            List[Dict]: List of coin data with name, symbol, priceUsd, priceChange24h, imageUrl
        """
        try:
            # Build URL with comma-separated addresses
            addresses_str = ",".join(self.coin_addresses)
            url = f"{self.base_url}/{addresses_str}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"DexScreener API error: {response.status}")
                        return self._get_fallback_data()
                    
                    data = await response.json()
                    
                    # Parse DexScreener response
                    pairs = data.get("pairs", [])
                    if not pairs:
                        logger.warning("No pairs found in DexScreener response")
                        return self._get_fallback_data()
                    
                    # Group by token address and get the best pair (highest liquidity)
                    # Create a case-insensitive mapping of addresses
                    address_map = {addr.upper(): addr for addr in self.coin_addresses}
                    coin_map = {}
                    
                    for pair in pairs:
                        base_token = pair.get("baseToken", {})
                        token_address = base_token.get("address", "")
                        token_address_upper = token_address.upper()
                        
                        # Check if this token address matches any of our target addresses (case-insensitive)
                        if token_address_upper in address_map:
                            # Use the pair with highest liquidity
                            liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                            
                            # Use uppercase address as key for consistency
                            if token_address_upper not in coin_map:
                                coin_map[token_address_upper] = {
                                    "liquidity": liquidity_usd,
                                    "pair": pair,
                                    "original_address": token_address
                                }
                            elif liquidity_usd > coin_map[token_address_upper]["liquidity"]:
                                coin_map[token_address_upper] = {
                                    "liquidity": liquidity_usd,
                                    "pair": pair,
                                    "original_address": token_address
                                }
                    
                    # Build result list
                    result = []
                    for address_upper, coin_data in coin_map.items():
                        pair = coin_data["pair"]
                        base_token = pair.get("baseToken", {})
                        
                        coin_info = {
                            "name": base_token.get("name", "Unknown"),
                            "symbol": base_token.get("symbol", "UNKNOWN"),
                            "priceUsd": pair.get("priceUsd", "0"),
                            "priceChange24h": pair.get("priceChange", {}).get("h24", 0),
                            "imageUrl": base_token.get("logoURI", ""),
                            "address": coin_data.get("original_address", address_upper),
                            "volume24h": pair.get("volume", {}).get("h24", 0),
                            "liquidity": coin_data["liquidity"]
                        }
                        result.append(coin_info)
                    
                    # Sort by symbol for consistent ordering
                    result.sort(key=lambda x: x["symbol"])
                    
                    if not result:
                        return self._get_fallback_data()
                    
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching coin data: {str(e)}")
            return self._get_fallback_data()
        except Exception as e:
            logger.error(f"Error fetching coin data: {str(e)}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> List[Dict]:
        """
        Fallback data in case API fails (still real structure, but with placeholder values)
        This should rarely be used, but provides graceful degradation
        """
        logger.warning("Using fallback coin data")
        return [
            {
                "name": "Bonk",
                "symbol": "BONK",
                "priceUsd": "0",
                "priceChange24h": 0,
                "imageUrl": "",
                "address": SOLANA_MEME_COINS["BONK"],
                "volume24h": 0,
                "liquidity": 0
            },
            {
                "name": "dogwifhat",
                "symbol": "WIF",
                "priceUsd": "0",
                "priceChange24h": 0,
                "imageUrl": "",
                "address": SOLANA_MEME_COINS["WIF"],
                "volume24h": 0,
                "liquidity": 0
            },
            {
                "name": "Popcat",
                "symbol": "POPCAT",
                "priceUsd": "0",
                "priceChange24h": 0,
                "imageUrl": "",
                "address": SOLANA_MEME_COINS["POPCAT"],
                "volume24h": 0,
                "liquidity": 0
            }
        ]

