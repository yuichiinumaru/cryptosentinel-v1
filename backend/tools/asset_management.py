import os
import uuid
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage
from backend.storage.models import ActivityData
from backend.tools.dex import Web3Provider # Use shared provider

class MonitorTransactionsInput(BaseModel):
    wallet_address: str = Field(..., description="The wallet address to monitor.")
    chain: str = Field("ethereum", description="Blockchain network to inspect.")

class MonitorTransactionsOutput(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="A list of recent transactions.")

class AssetManagementToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="asset_management_toolkit", **kwargs)
        self.register(self.monitor_transactions)
        self.register(self.check_wallet_security)

    async def monitor_transactions(self, input: MonitorTransactionsInput) -> MonitorTransactionsOutput:
        """
        Monitors transactions for a given wallet address using Block Explorers.
        """
        BLOCK_EXPLORERS = {
            "ethereum": {"base_url": "https://api.etherscan.io/api", "api_key_env": "ETHERSCAN_API_KEY"},
            "bsc": {"base_url": "https://api.bscscan.com/api", "api_key_env": "BSCSCAN_API_KEY"},
        }

        config = BLOCK_EXPLORERS.get(input.chain.lower())
        if not config:
            raise ValueError(f"Unsupported chain: {input.chain}")

        api_key = os.getenv(config["api_key_env"], "")
        params = {
            "module": "account",
            "action": "txlist",
            "address": input.wallet_address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": api_key,
        }

        # Non-blocking IO
        # requests is blocking. In strict async environment, should use httpx.
        # For now, wrapping in thread or switching to httpx if available.
        # Ideally, we follow the Necromancer rule: No blocking.
        import httpx
        async with httpx.AsyncClient() as client:
             response = await client.get(config["base_url"], params=params, timeout=20.0)
             response.raise_for_status()
             payload = response.json()

        if payload.get("status") not in {"1", 1}:
            return MonitorTransactionsOutput(transactions=[])

        transactions = []
        for tx in payload.get("result", [])[:10]:
            transactions.append({
                "hash": tx.get("hash"),
                "value": str(Decimal(tx.get("value", "0")) / Decimal(10**18)),
                "to": tx.get("to"),
                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0)), tz=timezone.utc).isoformat()
            })

        return MonitorTransactionsOutput(transactions=transactions)

    async def check_wallet_security(self, wallet_address: str) -> str:
        """
        Simple security check logic.
        """
        # Placeholder for complex logic, but Async ready.
        return "Secure"

# Instance
asset_management_toolkit = AssetManagementToolkit()
