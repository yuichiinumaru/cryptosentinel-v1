import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.market_data import fetch_market_data
from backend.tools.token_security import check_token_security
from backend.tools.technical_analysis import technical_analysis_toolkit
from backend.tools.alerting import alerting_toolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

market_analyst = Agent(
    id="market_analyst",
    name="MarketAnalyst",
    description="Analisa dados de mercado, verifica a segurança dos tokens e fornece recomendações de trading.",
    instructions=instructions,
    tools=[fetch_market_data, check_token_security, technical_analysis_toolkit, alerting_toolkit],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
