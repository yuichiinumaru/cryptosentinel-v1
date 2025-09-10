from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.dev import (
    DevelopmentEnvironmentTool,
    VersionControlTool,
    ContainerizationTool,
    CICDTool,
    DependencyManagementTool,
    TestingFrameworkTool,
    ProjectManagementTool,
    DocumentationGeneratorTool,
)
from backend.tools.asset_management import SystemMonitoringTool

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
with open("backend/Dev/instructions.md", "r") as f:
    instructions = f.read()

dev_agent = Agent(
    name="Dev",
    model=shared_model,
    tools=[
        DevelopmentEnvironmentTool,
        VersionControlTool,
        ContainerizationTool,
        CICDTool,
        SystemMonitoringTool,
        DependencyManagementTool,
        TestingFrameworkTool,
        ProjectManagementTool,
        DocumentationGeneratorTool,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=True,
)

if __name__ == "__main__":
    # Example usage
    response = dev_agent.run("Create a new tool for the MarketAnalyst.")
    print(response)
