from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.dex import ExecuteSwap, ExecuteTransactionSimulation, RevokeApprovalTool
from backend.tools.cex import ExecuteOrder, GetOrderBook
from backend.tools.wallet import GetAccountBalance, GetGasPrice, GetTransactionReceipt
from backend.tools.market_data import FetchMarketData

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
with open("backend/Trader/instructions.md", "r") as f:
    instructions = f.read()

trader_agent = Agent(
    name="Trader",
    model=shared_model,
    tools=[
        ExecuteSwap,
        ExecuteOrder,
        GetAccountBalance,
        GetTransactionReceipt,
        RevokeApprovalTool,
        ExecuteTransactionSimulation,
        GetOrderBook,
        GetGasPrice,
        FetchMarketData,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
    parallel_tool_calls=False,
)

if __name__ == "__main__":
    # Example usage
    response = trader_agent.run("Execute a swap of 1 ETH for DAI on Uniswap V2.")
    print(response)
