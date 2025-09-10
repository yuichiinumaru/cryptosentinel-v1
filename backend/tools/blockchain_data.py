import os
import requests
from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool


class FetchBlockchainDataInput(BaseModel):
    address: str = Field(..., description="The address to fetch data for.")
    module: str = Field("account", description="The Etherscan API module to use.")
    action: str = Field("balance", description="The action to perform.")
    chain: str = Field("mainnet", description="The blockchain to fetch data from.")


class FetchBlockchainDataOutput(BaseModel):
    data: Dict[str, Any] = Field(..., description="A dictionary containing the blockchain data.")


@tool(input_schema=FetchBlockchainDataInput, output_schema=FetchBlockchainDataOutput)
def FetchBlockchainDataTool(address: str, module: str = "account", action: str = "balance", chain: str = "mainnet") -> Dict[str, Any]:
    """
    Fetches data from a blockchain explorer like Etherscan.
    """
    etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
    if not etherscan_api_key:
        return {"data": {}}

    base_url = f"https://api.etherscan.io/api"
    if chain != "mainnet":
        base_url = f"https://api-{chain}.etherscan.io/api"

    params = {
        "module": module,
        "action": action,
        "address": address,
        "apikey": etherscan_api_key,
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    return {"data": data}
