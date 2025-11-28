import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.learning import learning_toolkit
from backend.tools.portfolio import get_portfolio

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

learning_coordinator = Agent(
    id="learning_coordinator",
    name="Learning Coordinator",
    description="Analisa o desempenho do sistema e ajusta as estratégias dos outros agentes para aprendizado contínuo.",
    instructions=instructions,
    tools=[learning_toolkit, get_portfolio],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
