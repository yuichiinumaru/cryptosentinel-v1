from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.portfolio import GetPortfolio, CalculatePortfolioMetrics, CalculatePortfolioRisk, GetTradeHistoryFromDB
from backend.tools.market_data import FetchMarketData
from backend.tools.wallet import GetAccountBalance

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Agent Configuration
model_name = os.getenv("gemini_model", "gemini-1.5-flash-latest")
temperature = float(os.getenv("temperature", 0.7))
api_key = os.getenv("GEMINI_API_KEY")

shared_model = Gemini(
    id=model_name,
    api_key=api_key,
    temperature=temperature,
)

# Load instructions from file
with open("backend/PortfolioManager/instructions.md", "r") as f:
    instructions = f.read()

portfolio_manager = Agent(
    name="PortfolioManager",
    model=shared_model,
    tools=[
        GetPortfolio,
        FetchMarketData,
        CalculatePortfolioMetrics,
        CalculatePortfolioRisk,
        GetAccountBalance,
        GetTradeHistoryFromDB,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = portfolio_manager.run("Get the portfolio.")
    print(response)
