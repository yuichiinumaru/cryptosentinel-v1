import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.risk_management import RiskManagementToolkit
from backend.tools.strategy import StrategyToolkit
from backend.tools.market_data import fetch_market_data

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

deep_trader_manager = Agent(
    id="deep_trader_manager",
    name="DeepTraderManager",
    description="Gerencia a equipe DeepTrader, define metas, monitora riscos e otimiza a alocação de capital.",
    instructions=instructions,
    tools=[RiskManagementToolkit(), StrategyToolkit(), fetch_market_data],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
