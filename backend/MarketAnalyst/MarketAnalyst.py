from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.market_data import FetchMarketData
from backend.tools.token_security import CheckTokenSecurity
from backend.tools.technical_analysis import CalculateTechnicalIndicator

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
with open("backend/MarketAnalyst/instructions.md", "r") as f:
    instructions = f.read()

market_analyst = Agent(
    name="MarketAnalyst",
    model=shared_model,
    tools=[
        FetchMarketData,
        CheckTokenSecurity,
        CalculateTechnicalIndicator,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = market_analyst.run("Analyze the market for BTC and ETH.")
    print(response)
