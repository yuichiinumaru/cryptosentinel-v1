from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool
from pycoingecko import CoinGeckoAPI


class FetchFundamentalDataInput(BaseModel):
    coin_id: str = Field(..., description="The ID of the coin from CoinGecko.")


class FetchFundamentalDataOutput(BaseModel):
    data: Dict[str, Any] = Field(..., description="A dictionary containing the fundamental data.")


@tool(input_schema=FetchFundamentalDataInput, output_schema=FetchFundamentalDataOutput)
def FetchFundamentalDataTool(coin_id: str) -> Dict[str, Any]:
    """
    Fetches fundamental data for a cryptocurrency from CoinGecko.
    """
    cg = CoinGeckoAPI()
    try:
        data = cg.get_coin_by_id(id=coin_id)
        return {"data": data}
    except Exception as e:
        return {"data": {}, "error": f"Could not fetch data: {e}"}
