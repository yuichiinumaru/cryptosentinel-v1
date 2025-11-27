import os
from agno.agent import Agent
from backend.tools.dev import dev_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

dev_agent = Agent(
    id="dev",
    name="Dev",
    description="Desenvolve e mantém as ferramentas e a infraestrutura do sistema.",
    instructions=instructions,
    tools=[dev_toolkit],
    model=get_shared_model(),
)
