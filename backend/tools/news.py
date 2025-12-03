import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class FetchNewsInput(BaseModel):
    query: str = Field(..., description="The query to search for news articles.")
    source: str = Field("google", description="News source: 'google' or 'cryptocompare'.")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of articles to return.")


class FetchNewsOutput(BaseModel):
    articles: List[Dict[str, Any]] = Field(..., description="List of news articles.")


def _fetch_google_news(query: str, limit: int) -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    from xml.etree import ElementTree as ET

    root = ET.fromstring(response.content)
    articles: List[Dict[str, Any]] = []
    for item in root.findall("channel/item")[:limit]:
        articles.append(
            {
                "title": item.findtext("title"),
                "url": item.findtext("link"),
                "published_at": item.findtext("pubDate"),
                "source": item.findtext("source"),
                "platform": "google",
            }
        )
    return articles


def _fetch_cryptocompare_news(limit: int) -> List[Dict[str, Any]]:
    url = "https://min-api.cryptocompare.com/data/v2/news/"
    response = requests.get(url, params={"lang": "EN"}, timeout=10)
    response.raise_for_status()
    data = response.json()
    articles: List[Dict[str, Any]] = []
    for item in data.get("Data", [])[:limit]:
        articles.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "source": item.get("source"),
                "published_at": datetime.utcfromtimestamp(item.get("published_on", 0)).isoformat() if item.get("published_on") else None,
                "tags": item.get("tags"),
                "platform": "cryptocompare",
            }
        )
    return articles


def fetch_news(input: FetchNewsInput) -> FetchNewsOutput:
    source = input.source.lower()
    if source == "cryptocompare":
        articles = _fetch_cryptocompare_news(input.limit)
    else:
        articles = _fetch_google_news(input.query, input.limit)
    return FetchNewsOutput(articles=articles)


news_toolkit = Toolkit(name="news")
news_toolkit.register(fetch_news)
