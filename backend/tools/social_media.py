from pydantic import BaseModel, Field
from typing import List, Dict, Any
from agno.tools.toolkit import Toolkit


class FetchSocialMediaInput(BaseModel):
    query: str = Field(..., description="The query to search for on social media.")
    platform: str = Field("twitter", description="The social media platform to search on ('twitter' or 'reddit').")


class FetchSocialMediaOutput(BaseModel):
    posts: List[Dict[str, Any]] = Field(..., description="A list of social media posts.")


def fetch_social_media(input: FetchSocialMediaInput) -> FetchSocialMediaOutput:
    """
    Fetches data from social media platforms like X (Twitter) and Reddit.
    """
    # ... (Placeholder implementation)
    return FetchSocialMediaOutput(posts=[{"text": f"Social media post about {input.query} on {input.platform}", "user": "placeholder_user"}])

import os
from datetime import datetime
from typing import List, Dict, Any

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class FetchSocialMediaInput(BaseModel):
    query: str = Field(..., description="The query to search for on social media.")
    platform: str = Field("twitter", description="The social media platform to search on ('twitter' or 'reddit').")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of posts to fetch.")


class FetchSocialMediaOutput(BaseModel):
    posts: List[Dict[str, Any]] = Field(..., description="A list of social media posts.")


def _fetch_twitter(query: str, limit: int) -> List[Dict[str, Any]]:
    bearer = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer:
        raise ValueError("TWITTER_BEARER_TOKEN environment variable is required for Twitter searches.")
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,author_id,lang",
    }
    headers = {"Authorization": f"Bearer {bearer}"}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    payload = response.json()
    posts = []
    for item in payload.get("data", []):
        posts.append(
            {
                "id": item.get("id"),
                "text": item.get("text"),
                "user": item.get("author_id"),
                "timestamp": item.get("created_at"),
                "language": item.get("lang"),
                "platform": "twitter",
                "url": f"https://twitter.com/i/web/status/{item.get('id')}" if item.get("id") else None,
            }
        )
    return posts


def _fetch_reddit(query: str, limit: int) -> List[Dict[str, Any]]:
    headers = {"User-Agent": "CryptoSentinel/1.0"}
    params = {
        "q": query,
        "limit": limit,
        "sort": "new",
        "restrict_sr": False,
        "include_over_18": False,
    }
    response = requests.get("https://www.reddit.com/search.json", params=params, headers=headers, timeout=10)
    response.raise_for_status()
    payload = response.json()
    posts = []
    for child in payload.get("data", {}).get("children", []):
        data = child.get("data", {})
        posts.append(
            {
                "id": data.get("id"),
                "text": data.get("title"),
                "user": data.get("author"),
                "timestamp": datetime.utcfromtimestamp(data.get("created_utc", 0)).isoformat() if data.get("created_utc") else None,
                "platform": "reddit",
                "url": f"https://reddit.com{data.get('permalink')}" if data.get("permalink") else None,
                "score": data.get("score"),
                "subreddit": data.get("subreddit"),
            }
        )
    return posts


def fetch_social_media(input: FetchSocialMediaInput) -> FetchSocialMediaOutput:
    """Fetch data from social media platforms like X (Twitter) and Reddit."""
    platform = input.platform.lower()
    if platform == "twitter":
        posts = _fetch_twitter(input.query, input.limit)
    elif platform == "reddit":
        posts = _fetch_reddit(input.query, input.limit)
    else:
        raise ValueError(f"Unsupported social media platform: {input.platform}")
    return FetchSocialMediaOutput(posts=posts)


social_media_toolkit = Toolkit(name="social_media")
social_media_toolkit.register(fetch_social_media)
