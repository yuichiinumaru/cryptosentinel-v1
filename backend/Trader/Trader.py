import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.dex import execute_swap
from backend.tools.portfolio import get_portfolio
from backend.tools.wallet import get_account_balance

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

trader_agent = Agent(
    id="trader_agent",
    name="Trader",
    description="Executa ordens de compra e venda em DEXs e CEXs, e gerencia o portfólio.",
    instructions=instructions,
    tools=[execute_swap, get_portfolio, get_account_balance],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
