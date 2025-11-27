import os
from agno.agent import Agent
from backend.tools.risk_management import risk_management_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

risk_analyst = Agent(
    id="risk_analyst",
    name="RiskAnalyst",
    description="Monitora e avalia riscos do portfólio, incluindo volatilidade, liquidez e exposições concentradas.",
    instructions=instructions,
    tools=[risk_management_toolkit],
    model=get_shared_model(),
)
