from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.risk_management import CalculateRiskMetricsTool, ManageBlacklistTool, DetectAnomaliesTool, StressTestingTool
from backend.tools.token_security import CheckTokenSecurity
from backend.tools.alerting import SendInternalAlertTool
from backend.tools.dex import ExecuteTransactionSimulation
from backend.tools.portfolio import GetPortfolio

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
with open("backend/RiskAnalyst/instructions.md", "r") as f:
    instructions = f.read()

risk_analyst = Agent(
    name="RiskAnalyst",
    model=shared_model,
    tools=[
        CalculateRiskMetricsTool,
        CheckTokenSecurity,
        ManageBlacklistTool,
        DetectAnomaliesTool,
        SendInternalAlertTool,
        ExecuteTransactionSimulation,
        StressTestingTool,
        GetPortfolio,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = risk_analyst.run("Calculate the risk metrics for the portfolio.")
    print(response)
