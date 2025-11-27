import os
from agno.agent import Agent
from backend.tools.portfolio import get_portfolio
from backend.tools.portfolio_analysis import portfolio_analysis_toolkit
from backend.tools.risk_management import risk_management_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

portfolio_manager = Agent(
    id="portfolio_manager",
    name="PortfolioManager",
    description="Gerencia o portfólio, define alocação de capital, calcula o risco e monitora o desempenho.",
    instructions=instructions,
    tools=[get_portfolio, portfolio_analysis_toolkit, risk_management_toolkit],
    model=get_shared_model(),
)
