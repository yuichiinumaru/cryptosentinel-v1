from typing import Dict, Any

from agno.tools.toolkit import Toolkit
from pycoingecko import CoinGeckoAPI
from pydantic import BaseModel, Field


class FetchFundamentalDataInput(BaseModel):
    coin_id: str = Field(..., description="CoinGecko identifier of the asset.")


class FetchFundamentalDataOutput(BaseModel):
    data: Dict[str, Any] = Field(..., description="Fundamental data payload.")
    error: str | None = Field(None, description="Error message when retrieval fails.")


def fetch_fundamental_data(input: FetchFundamentalDataInput) -> FetchFundamentalDataOutput:
    client = CoinGeckoAPI()
    try:
        data = client.get_coin_by_id(id=input.coin_id)
        return FetchFundamentalDataOutput(data=data, error=None)
    except Exception as exc:
        return FetchFundamentalDataOutput(data={}, error=str(exc))


fundamental_data_toolkit = Toolkit(name="fundamental_data")
fundamental_data_toolkit.register(fetch_fundamental_data)
