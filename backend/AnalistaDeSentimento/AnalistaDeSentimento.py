import os
from agno.agent import Agent
from agno.models.google import Gemini
from backend.tools.social_media import SocialMediaToolkit

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

analista_de_sentimento = Agent(
    id="analista_de_sentimento",
    name="Analista de Sentimento de Mercado",
    description="Analisa o sentimento do mercado em relação a criptomoedas.",
    instructions=instructions,
    tools=[SocialMediaToolkit()],
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=os.getenv("gemini_api_key"),
        temperature=float(os.getenv("temperature", 0.7)),
    ),
)
