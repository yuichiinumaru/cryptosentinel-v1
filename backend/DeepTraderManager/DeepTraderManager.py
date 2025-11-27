import os
from agno.agent import Agent
from backend.tools.risk_management import risk_management_toolkit
from backend.tools.strategy import strategy_toolkit
from backend.tools.market_data import market_data_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

deep_trader_manager = Agent(
    id="deep_trader_manager",
    name="DeepTraderManager",
    description="Gerencia a equipe DeepTrader, define metas, monitora riscos e otimiza a alocação de capital.",
    instructions=instructions,
    tools=[risk_management_toolkit, strategy_toolkit, market_data_toolkit],
    model=get_shared_model(),
)
