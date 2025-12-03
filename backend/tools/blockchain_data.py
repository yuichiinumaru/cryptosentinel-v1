import os
from typing import Dict, Any

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class FetchBlockchainDataInput(BaseModel):
    address: str = Field(..., description="Target address to inspect.")
    module: str = Field("account", description="Explorer module (e.g., account, txlist).")
    action: str = Field("balance", description="Action to perform within the module.")
    chain: str = Field("mainnet", description="Ethereum network name (mainnet, goerli, etc.).")


class FetchBlockchainDataOutput(BaseModel):
    data: Dict[str, Any] = Field(..., description="Explorer API payload.")
    error: str | None = Field(None, description="Error details when retrieval fails.")


def fetch_blockchain_data(input: FetchBlockchainDataInput) -> FetchBlockchainDataOutput:
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        return FetchBlockchainDataOutput(data={}, error="ETHERSCAN_API_KEY not configured")

    base_url = "https://api.etherscan.io/api" if input.chain == "mainnet" else f"https://api-{input.chain}.etherscan.io/api"
    params = {
        "module": input.module,
        "action": input.action,
        "address": input.address,
        "apikey": api_key,
    }
    try:
        response = requests.get(base_url, params=params, timeout=20)
        response.raise_for_status()
        return FetchBlockchainDataOutput(data=response.json(), error=None)
    except Exception as exc:
        return FetchBlockchainDataOutput(data={}, error=str(exc))


blockchain_data_toolkit = Toolkit(name="blockchain_data")
blockchain_data_toolkit.register(fetch_blockchain_data)
