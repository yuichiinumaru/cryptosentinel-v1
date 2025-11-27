import os
from agno.agent import Agent
from backend.tools.strategy import strategy_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

strategy_agent = Agent(
    id="strategy_agent",
    name="StrategyAgent",
    description="Desenvolve, testa e otimiza estratégias de trading.",
    instructions=instructions,
    tools=[strategy_toolkit],
    model=get_shared_model(),
)
