import os
from agno.agent import Agent
from backend.tools.learning import learning_toolkit
from backend.tools.portfolio import get_portfolio
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

learning_coordinator = Agent(
    id="learning_coordinator",
    name="Learning Coordinator",
    description="Analisa o desempenho do sistema e ajusta as estratégias dos outros agentes para aprendizado contínuo.",
    instructions=instructions,
    tools=[learning_toolkit, get_portfolio],
    model=get_shared_model(),
)
