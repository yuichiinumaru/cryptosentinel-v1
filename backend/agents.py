import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime
import json

from agno.agent import Agent
from agno.team import Team
from agno.models.google import Gemini
from agno.tools import tool
from agno.tools.duckduckgo import DuckDuckGoTools

from backend.storage import SqliteStorage
from backend.storage.base import Storage
from backend.storage.models import TradeData, ActivityData


def get_storage() -> Storage:
    storage_type = os.getenv("STORAGE_TYPE", "sqlite")
    storage_url = os.getenv("STORAGE_URL", "sqlite.db")

    if storage_type == "sqlite":
        return SqliteStorage(storage_url)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")


storage = get_storage()


class KeyManager:
    def __init__(self):
        load_dotenv()
        self.api_keys = self._load_keys()
        if not self.api_keys:
            raise ValueError("No Gemini API keys found in .env file.")
        self.current_key_index = 0

    def _load_keys(self) -> list[str]:
        keys_str = os.getenv("gemini_api_keys")
        if keys_str:
            return [key.strip() for key in keys_str.split(',')]
        return []

    def get_key(self) -> str:
        return self.api_keys[self.current_key_index]

    def rotate_key(self) -> str:
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Rotated to new API key index: {self.current_key_index}")
        return self.get_key()


key_manager = KeyManager()

model_name = os.getenv("gemini_model", "gemini-1.5-flash-latest")
temperature = float(os.getenv("temperature", 0.7))

shared_model = Gemini(
    id=model_name,
    api_key=key_manager.get_key(),
    temperature=temperature,
)


@tool
def record_trade_tool(token: str, action: str, amount: float, price: float, status: str, profit: float = 0.0) -> str:
    trade_data = TradeData(
        id=f"trade_{int(datetime.now().timestamp())}",
        token=token,
        action=action,
        amount=amount,
        price=price,
        timestamp=datetime.now(),
        profit=profit,
        status=status,
    )
    storage.add_trade(trade_data)
    activity_data = ActivityData(
        id=f"activity_{int(datetime.now().timestamp())}",
        timestamp=datetime.now(),
        type="trade_execution",
        message=f"Recorded {action} trade of {amount} {token} at ${price}",
        details={"status": status},
    )
    storage.add_activity(activity_data)
    return f"Successfully recorded {action} of {amount} {token}."


@tool
def record_activity_tool(type: str, message: str, details: dict = None) -> str:
    activity_data = ActivityData(
        id=f"activity_{int(datetime.now().timestamp())}",
        timestamp=datetime.now(),
        type=type,
        message=message,
        details=details or {},
    )
    storage.add_activity(activity_data)
    return "Successfully recorded activity."


market_analyst = Agent(name="MarketAnalyst", model=shared_model, tools=[DuckDuckGoTools(search=True, news=True), record_activity_tool], instructions=["..."])
trader_agent = Agent(name="Trader", model=shared_model, tools=[record_trade_tool], instructions=["..."])
learning_manager = Agent(name="LearningManager", model=shared_model, tools=[record_activity_tool], instructions=["..."])
manager_agent = Agent(name="Manager", model=shared_model, tools=[], instructions=["..."])

crypto_trading_team = Team(
    members=[manager_agent, market_analyst, trader_agent, learning_manager],
    name="CryptoSentinelTeam",
    model=shared_model,
)
