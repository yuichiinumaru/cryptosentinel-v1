from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.asset_management import MonitorTransactionsTool, CheckWalletSecurityTool, SystemMonitoringTool, SecureTransferTool, FetchSecretTool
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
with open("backend/AssetManager/instructions.md", "r") as f:
    instructions = f.read()

asset_manager = Agent(
    name="AssetManager",
    model=shared_model,
    tools=[
        MonitorTransactionsTool,
        CheckWalletSecurityTool,
        SystemMonitoringTool,
        SecureTransferTool,
        GetAccountBalance,
        FetchSecretTool,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = asset_manager.run("Check the security of the main wallet.")
    print(response)
