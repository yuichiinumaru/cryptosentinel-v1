import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.news import news_toolkit
from backend.tools.sentiment_analysis import sentiment_analysis_toolkit
from backend.tools.alerting import alerting_toolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

analista_fundamentalista = Agent(
    id="analista_fundamentalista",
    name="Analista Fundamentalista",
    description="Analisa os fundamentos de criptomoedas, como notícias, whitepapers e equipes.",
    instructions=instructions,
    tools=[news_toolkit, sentiment_analysis_toolkit, alerting_toolkit],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
