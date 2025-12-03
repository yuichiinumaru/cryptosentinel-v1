from pydantic import BaseModel, Field
from typing import Dict
from agno.tools.toolkit import Toolkit
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download the VADER lexicon if it's not already downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:  # pragma: no cover - depends on environment state
    nltk.download('vader_lexicon')

class AnalyzeSentimentInput(BaseModel):
    text: str = Field(..., description="The text to analyze.")

class AnalyzeSentimentOutput(BaseModel):
    sentiment: Dict[str, float] = Field(..., description="A dictionary containing the sentiment scores.")

def analyze_sentiment(input: AnalyzeSentimentInput) -> AnalyzeSentimentOutput:
    """
    Analyzes the sentiment of a given text using NLTK's VADER.
    """
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(input.text)
    return AnalyzeSentimentOutput(sentiment=sentiment_scores)

sentiment_analysis_toolkit = Toolkit(name="sentiment_analysis")
sentiment_analysis_toolkit.register(analyze_sentiment)
