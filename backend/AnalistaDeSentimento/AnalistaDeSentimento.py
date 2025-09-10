from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.social_media import FetchSocialMediaTool
from backend.tools.news import FetchNewsTool
from backend.tools.sentiment_analysis import AnalyzeSentimentTool
from backend.tools.alerting import SendInternalAlertTool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Agent Configuration
model_name = os.getenv("gemini_model", "gemini-1.5-flash-latest")
temperature = float(os.getenv("temperature", 0.7))
api_key = os.getenv("GEMINI_API_KEY")

shared_model = Gemini(
    id=model_name,
    api_key=api_key,
    temperature=temperature,
)

# Load instructions from file
with open("backend/AnalistaDeSentimento/instructions.md", "r") as f:
    instructions = f.read()

analista_de_sentimento = Agent(
    name="AnalistaDeSentimento",
    model=shared_model,
    tools=[
        FetchSocialMediaTool,
        FetchNewsTool,
        AnalyzeSentimentTool,
        SendInternalAlertTool,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = analista_de_sentimento.run("Analyze the sentiment around Bitcoin.")
    print(response)
