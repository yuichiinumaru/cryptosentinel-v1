import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.risk_management import RiskManagementToolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

risk_analyst = Agent(
    id="risk_analyst",
    name="RiskAnalyst",
    description="Monitora e avalia riscos do portfólio, incluindo volatilidade, liquidez e exposições concentradas.",
    instructions=instructions,
    tools=[RiskManagementToolkit()],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
