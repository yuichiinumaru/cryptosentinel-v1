from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.portfolio import GetPortfolio
from backend.tools.wallet import GetAccountBalance
from backend.tools.communication import ApproveTradeTool, RejectTradeTool
from backend.tools.risk_management import AdjustGlobalRiskParameters, PauseTradingTool

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
with open("backend/DeepTraderManager/instructions.md", "r") as f:
    instructions = f.read()

deep_trader_manager = Agent(
    name="DeepTraderManager",
    model=shared_model,
    tools=[
        GetPortfolio,
        GetAccountBalance,
        ApproveTradeTool,
        RejectTradeTool,
        AdjustGlobalRiskParameters,
        PauseTradingTool,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = deep_trader_manager.run("Approve trade 123.")
    print(response)
