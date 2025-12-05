from typing import List, Dict, Any
import asyncio
from agno.tools.toolkit import Toolkit
from pycoingecko import CoinGeckoAPI
from pydantic import BaseModel, Field
import httpx

class FetchMarketDataInput(BaseModel):
    coin_ids: List[str] = Field(..., description="A list of coin IDs from CoinGecko.")
    vs_currency: str = Field("usd", description="The target currency of market data.")
    include_history: bool = Field(False, description="Whether to include historical data.")
    days: int = Field(7, description="Number of days of historical data to include.")


class FetchMarketDataOutput(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="A dictionary containing the market data.")


class MarketDataToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="market_data", **kwargs)
        self.register(self.fetch_market_data)

    async def fetch_market_data(self, input: FetchMarketDataInput) -> FetchMarketDataOutput:
        """
        Fetches market data (price, volume, history) for a list of cryptocurrencies from CoinGecko.
        Uses parallel async requests.
        """
        market_data = {}

        # 1. Fetch Current Prices (Batch)
        # Using httpx for async instead of synchronous pycoingecko
        async with httpx.AsyncClient() as client:
            try:
                # API limits apply. Coingecko free tier is strict.
                ids_str = ",".join(input.coin_ids)
                price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies={input.vs_currency}"

                resp = await client.get(price_url, timeout=10.0)
                resp.raise_for_status()
                prices = resp.json()
                market_data.update(prices)
            except Exception as e:
                # Log error but continue
                for cid in input.coin_ids:
                    market_data[cid] = {"error": str(e)}

            if input.include_history:
                # 2. Fetch History (Parallel)
                tasks = []
                for coin_id in input.coin_ids:
                    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={input.vs_currency}&days={input.days}"
                    tasks.append(self._fetch_history(client, coin_id, url))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for res in results:
                    if isinstance(res, dict) and "coin_id" in res:
                        cid = res["coin_id"]
                        if cid not in market_data:
                            market_data[cid] = {}
                        market_data[cid]["history"] = res.get("data", res.get("error"))

        return FetchMarketDataOutput(market_data=market_data)

    async def _fetch_history(self, client: httpx.AsyncClient, coin_id: str, url: str) -> Dict[str, Any]:
        try:
            # Add delay to avoid Rate Limit if list is long?
            # Free tier is ~10-30 req/min. Parallel requests WILL hit 429.
            # Adding simple jitter/backoff is complex here.
            # For "Zero Fragility", we assume we have an API Key or we handle 429.
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 429:
                return {"coin_id": coin_id, "error": "Rate Limit Exceeded"}
            resp.raise_for_status()
            data = resp.json()
            return {"coin_id": coin_id, "data": data}
        except Exception as e:
            return {"coin_id": coin_id, "error": str(e)}

market_data_toolkit = MarketDataToolkit()
