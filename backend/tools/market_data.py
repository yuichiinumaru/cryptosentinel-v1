from pydantic import BaseModel, Field
from typing import List, Dict, Any
from agno.tools import tool
from pycoingecko import CoinGeckoAPI


class FetchMarketDataInput(BaseModel):
    coin_ids: List[str] = Field(..., description="A list of coin IDs from CoinGecko.")
    vs_currency: str = Field("usd", description="The target currency of market data.")
    include_history: bool = Field(False, description="Whether to include historical data.")
    days: int = Field(7, description="Number of days of historical data to include.")


class FetchMarketDataOutput(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="A dictionary containing the market data.")


@tool(input_schema=FetchMarketDataInput, output_schema=FetchMarketDataOutput)
def FetchMarketData(coin_ids: List[str], vs_currency: str = "usd", include_history: bool = False, days: int = 7) -> Dict[str, Any]:
    """
    Fetches market data (price, volume, history) for a list of cryptocurrencies from CoinGecko.
    """
    cg = CoinGeckoAPI()
    market_data = {}

    # Fetch current prices
    prices = cg.get_price(ids=coin_ids, vs_currencies=vs_currency)
    market_data.update(prices)

    if include_history:
        for coin_id in coin_ids:
            try:
                history = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
                market_data[coin_id]['history'] = history
            except Exception as e:
                market_data[coin_id]['history'] = f"Could not fetch history: {e}"

    return {"market_data": market_data}
