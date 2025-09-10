from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.learning import KnowledgeStorageTool, AnalyzeAgentPerformanceTool, AdjustAgentInstructionsTool, AdjustToolParametersTool
from backend.tools.portfolio import GetTradeHistoryFromDB, GetPortfolio

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
with open("backend/LearningCoordinator/instructions.md", "r") as f:
    instructions = f.read()

learning_coordinator = Agent(
    name="LearningCoordinator",
    model=shared_model,
    tools=[
        GetTradeHistoryFromDB,
        KnowledgeStorageTool,
        AnalyzeAgentPerformanceTool,
        AdjustAgentInstructionsTool,
        AdjustToolParametersTool,
        GetPortfolio,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=True,
)

if __name__ == "__main__":
    # Example usage
    response = learning_coordinator.run("Analyze the performance of the Trader agent.")
    print(response)
