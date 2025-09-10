from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.compliance import ComplianceCheckTool, CalculateFeesTool, GenerateFinancialReportsTool, RegulatoryWatchTool
from backend.tools.portfolio import GetTradeHistoryFromDB

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
with open("backend/ComplianceOfficer/instructions.md", "r") as f:
    instructions = f.read()

compliance_officer = Agent(
    name="ComplianceOfficer",
    model=shared_model,
    tools=[
        ComplianceCheckTool,
        CalculateFeesTool,
        GenerateFinancialReportsTool,
        RegulatoryWatchTool,
        GetTradeHistoryFromDB,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = compliance_officer.run("Generate a monthly financial report.")
    print(response)
