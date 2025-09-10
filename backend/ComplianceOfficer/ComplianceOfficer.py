import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.compliance import compliance_toolkit
from backend.tools.reporting import reporting_toolkit
from backend.tools.alerting import alerting_toolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

compliance_officer = Agent(
    id="compliance_officer",
    name="Compliance Officer",
    description="Garante que as operações de trading estejam em conformidade com as regulações.",
    instructions=instructions,
    tools=[compliance_toolkit, reporting_toolkit, alerting_toolkit],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
