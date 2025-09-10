from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.strategy import AnalyzePerformanceTool, FetchHistoricalDataTool, CheckArbitrageOpportunitiesTool, IdentifyMarketRegimeTool
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
with open("backend/StrategyAgent/instructions.md", "r") as f:
    instructions = f.read()

strategy_agent = Agent(
    name="StrategyAgent",
    model=shared_model,
    tools=[
        AnalyzePerformanceTool,
        FetchHistoricalDataTool,
        CheckArbitrageOpportunitiesTool,
        IdentifyMarketRegimeTool,
        CalculateTechnicalIndicator,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=True,
)

if __name__ == "__main__":
    # Example usage
    response = strategy_agent.run("Develop a trading strategy for BTC/USDT.")
    print(response)
