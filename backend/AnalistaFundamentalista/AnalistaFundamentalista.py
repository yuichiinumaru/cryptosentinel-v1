from agno.agent import Agent
from agno.models.google import Gemini
import os

from backend.tools.news import FetchNewsTool
from backend.tools.fundamental_data import FetchFundamentalDataTool
from backend.tools.document_analysis import AnalyzeDocumentTool
from backend.tools.blockchain_data import FetchBlockchainDataTool
from backend.tools.social_media import FetchSocialMediaTool

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
with open("backend/AnalistaFundamentalista/instructions.md", "r") as f:
    instructions = f.read()

analista_fundamentalista = Agent(
    name="AnalistaFundamentalista",
    model=shared_model,
    tools=[
        FetchNewsTool,
        FetchFundamentalDataTool,
        AnalyzeDocumentTool,
        FetchBlockchainDataTool,
        FetchSocialMediaTool,
    ],
    instructions=instructions,
    file_search=True,
    code_interpreter=False,
)

if __name__ == "__main__":
    # Example usage
    response = analista_fundamentalista.run("Analyze the fundamentals of Bitcoin.")
    print(response)
