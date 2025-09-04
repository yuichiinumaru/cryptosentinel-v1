import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from collections import deque
from datetime import datetime

from agno.agent import Agent
from agno.team import Team
from agno.models.google import Gemini
from agno.tools import tool
from agno.tools.duckduckgo import DuckDuckGoTools

# --- Merged from storage.py ---
MAX_ITEMS = 100
TradeData = Dict[str, Any]
ActivityData = Dict[str, Any]
trades_db: deque[TradeData] = deque(maxlen=MAX_ITEMS)
activities_db: deque[ActivityData] = deque(maxlen=MAX_ITEMS)

def add_trade(trade: TradeData):
    trades_db.appendleft(trade)

def get_recent_trades(limit: int) -> List[TradeData]:
    return list(trades_db)[:limit]

def add_activity(activity: ActivityData):
    activities_db.appendleft(activity)

def get_recent_activities(limit: int) -> List[ActivityData]:
    return list(activities_db)[:limit]

# --- Merged from key_manager.py ---
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

# --- Agent Configuration ---
model_name = os.getenv("gemini_model", "gemini-1.5-flash-latest")
temperature = float(os.getenv("temperature", 0.7))

shared_model = Gemini(
    id=model_name,
    api_key=key_manager.get_key(),
    temperature=temperature,
)

# --- Custom Tools ---
@tool
def record_trade_tool(token: str, action: str, amount: float, price: float, status: str, profit: float = 0.0) -> str:
    trade_data = {"id": f"trade_{int(datetime.now().timestamp())}", "token": token, "action": action, "amount": amount, "price": price, "timestamp": datetime.now().isoformat(), "profit": profit, "status": status}
    add_trade(trade_data)
    add_activity({"id": f"activity_{int(datetime.now().timestamp())}", "timestamp": datetime.now().isoformat(), "type": "trade_execution", "message": f"Recorded {action} trade of {amount} {token} at ${price}", "details": {"status": status}})
    return f"Successfully recorded {action} of {amount} {token}."

@tool
def record_activity_tool(type: str, message: str, details: dict = None) -> str:
    activity_data = {"id": f"activity_{int(datetime.now().timestamp())}", "timestamp": datetime.now().isoformat(), "type": type, "message": message, "details": details or {}}
    add_activity(activity_data)
    return "Successfully recorded activity."

# --- Agent Definitions ---
market_analyst = Agent(name="MarketAnalyst", model=shared_model, tools=[DuckDuckGoTools(search=True, news=True), record_activity_tool], instructions=["..."])
trader_agent = Agent(name="Trader", model=shared_model, tools=[record_trade_tool], instructions=["..."])
learning_manager = Agent(name="LearningManager", model=shared_model, tools=[record_activity_tool], instructions=["..."])
manager_agent = Agent(name="Manager", model=shared_model, tools=[], instructions=["..."])

# --- Team Definition ---
crypto_trading_team = Team(
    members=[manager_agent, market_analyst, trader_agent, learning_manager],
    name="CryptoSentinelTeam",
    model=shared_model,
)
