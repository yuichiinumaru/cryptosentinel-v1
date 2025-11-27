import os
from agno.agent import Agent
from backend.tools.news import news_toolkit
from backend.tools.sentiment_analysis import sentiment_analysis_toolkit
from backend.tools.alerting import alerting_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

analista_fundamentalista = Agent(
    id="analista_fundamentalista",
    name="Analista Fundamentalista",
    description="Analisa os fundamentos de criptomoedas, como notícias, whitepapers e equipes.",
    instructions=instructions,
    tools=[news_toolkit, sentiment_analysis_toolkit, alerting_toolkit],
    model=get_shared_model(),
)
