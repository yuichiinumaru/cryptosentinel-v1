from pydantic import BaseModel, Field
from typing import List, Dict, Any
from agno.tools.decorator import tool
from agno.tools.toolkit import Toolkit
from pycoingecko import CoinGeckoAPI


class FetchMarketDataInput(BaseModel):
    coin_ids: List[str] = Field(..., description="A list of coin IDs from CoinGecko.")
    vs_currency: str = Field("usd", description="The target currency of market data.")
    include_history: bool = Field(False, description="Whether to include historical data.")
    days: int = Field(7, description="Number of days of historical data to include.")


class FetchMarketDataOutput(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="A dictionary containing the market data.")


@tool
def fetch_market_data(input: FetchMarketDataInput) -> FetchMarketDataOutput:
    """
    Fetches market data (price, volume, history) for a list of cryptocurrencies from CoinGecko.
    """
    cg = CoinGeckoAPI()
    market_data = {}

    # Fetch current prices
    prices = cg.get_price(ids=input.coin_ids, vs_currencies=input.vs_currency)
    market_data.update(prices)

    if input.include_history:
        for coin_id in input.coin_ids:
            try:
                history = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=input.vs_currency, days=input.days)
                if coin_id in market_data:
                    market_data[coin_id]['history'] = history
                else:
                    market_data[coin_id] = {'history': history}
            except Exception as e:
                if coin_id in market_data:
                    market_data[coin_id]['history'] = f"Could not fetch history: {e}"
                else:
                    market_data[coin_id] = {'history': f"Could not fetch history: {e}"}


    return FetchMarketDataOutput(market_data=market_data)

market_data_toolkit = Toolkit(name="market_data")
