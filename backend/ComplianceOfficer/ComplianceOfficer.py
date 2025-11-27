import os
from agno.agent import Agent
from backend.tools.compliance import compliance_toolkit
from backend.tools.reporting import reporting_toolkit
from backend.tools.alerting import alerting_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

compliance_officer = Agent(
    id="compliance_officer",
    name="Compliance Officer",
    description="Garante que as operações de trading estejam em conformidade com as regulações.",
    instructions=instructions,
    tools=[compliance_toolkit, reporting_toolkit, alerting_toolkit],
    model=get_shared_model(),
)
