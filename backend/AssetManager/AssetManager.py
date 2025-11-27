import os
from agno.agent import Agent
from backend.tools.portfolio import get_portfolio
from backend.tools.wallet import get_account_balance
from backend.tools.alerting import alerting_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

asset_manager = Agent(
    id="asset_manager",
    name="Asset Manager",
    description="Gerencia os ativos da carteira, como alocação e rebalanceamento.",
    instructions=instructions,
    tools=[get_portfolio, get_account_balance, alerting_toolkit],
    model=get_shared_model(),
)
