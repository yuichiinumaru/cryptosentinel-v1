import os
import requests
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from agno.tools import tool


class FetchNewsInput(BaseModel):
    query: str = Field(..., description="The query to search for news.")
    sources: str = Field(None, description="A comma-separated string of news sources or domains.")


class FetchNewsOutput(BaseModel):
    articles: List[Dict[str, Any]] = Field(..., description="A list of news articles.")


@tool(input_schema=FetchNewsInput, output_schema=FetchNewsOutput)
def FetchNewsTool(query: str, sources: str = None) -> Dict[str, Any]:
    """
    Fetches news articles from a news API.
    """
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        return {"articles": []}

    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_key}"
    if sources:
        url += f"&sources={sources}"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    return {"articles": data.get("articles", [])}
