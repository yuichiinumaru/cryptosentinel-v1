import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.portfolio import get_portfolio
from backend.tools.wallet import wallet_toolkit
from backend.tools.alerting import alerting_toolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

asset_manager = Agent(
    id="asset_manager",
    name="Asset Manager",
    description="Gerencia os ativos da carteira, como alocação e rebalanceamento.",
    instructions=instructions,
    tools=[get_portfolio, wallet_toolkit, alerting_toolkit],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
