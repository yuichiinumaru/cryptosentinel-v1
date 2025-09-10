import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.dev import dev_toolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

dev_agent = Agent(
    id="dev",
    name="Dev",
    description="Desenvolve e mantém as ferramentas e a infraestrutura do sistema.",
    instructions=instructions,
    tools=[dev_toolkit],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
