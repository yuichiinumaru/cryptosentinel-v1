import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.portfolio import portfolio_toolkit
from backend.tools.portfolio_analysis import portfolio_analysis_toolkit
from backend.tools.risk_management import risk_management_toolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

portfolio_manager = Agent(
    id="portfolio_manager",
    name="PortfolioManager",
    description="Gerencia o portfólio, define alocação de capital, calcula o risco e monitora o desempenho.",
    instructions=instructions,
    tools=[portfolio_toolkit, portfolio_analysis_toolkit, risk_management_toolkit],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
