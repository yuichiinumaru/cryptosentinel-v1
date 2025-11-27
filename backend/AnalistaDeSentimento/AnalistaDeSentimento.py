import os
from agno.agent import Agent
from backend.tools.social_media import social_media_toolkit
from backend.shared_model import get_shared_model

# Load instructions from the markdown file
with open(os.path.join(os.path.dirname(__file__), 'instructions.md'), 'r') as f:
    instructions = f.read()

analista_de_sentimento = Agent(
    id="analista_de_sentimento",
    name="Analista de Sentimento de Mercado",
    description="Analisa o sentimento do mercado em relação a criptomoedas.",
    instructions=instructions,
    tools=[social_media_toolkit],
    model=get_shared_model(),
)
