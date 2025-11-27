import os
from agno.agent import Agent
from backend.tools.dex import execute_swap
from backend.tools.portfolio import get_portfolio
from backend.tools.wallet import get_account_balance
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

trader_agent = Agent(
    id="trader_agent",
    name="Trader",
    description="Executa ordens de compra e venda em DEXs e CEXs, e gerencia o portfólio.",
    instructions=instructions,
    tools=[execute_swap, get_portfolio, get_account_balance],
    model=get_shared_model(),
)
