from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download the VADER lexicon if not already downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')


class AnalyzeSentimentInput(BaseModel):
    text: str = Field(..., description="The text to analyze.")


class AnalyzeSentimentOutput(BaseModel):
    sentiment: Dict[str, float] = Field(..., description="A dictionary containing the sentiment scores.")


@tool(input_schema=AnalyzeSentimentInput, output_schema=AnalyzeSentimentOutput)
def AnalyzeSentimentTool(text: str) -> Dict[str, Any]:
    """
    Analyzes the sentiment of a given text using VADER.
    """
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(text)
    return {"sentiment": sentiment_scores}
