import os
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import json
import requests
from fastapi.responses import StreamingResponse

# --- Agent Team Import ---
from agno.tools.duckduckgo import DuckDuckGoTools
from backend.agents import (
    crypto_trading_team,
    get_recent_trades as db_get_recent_trades,
    get_recent_activities as db_get_recent_activities,
    key_manager
)


app = FastAPI(title="CryptoSentinel API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Dependency ---
async def get_api_key(authorization: str = Header(None)):
    """
    Gets the API key from the Authorization header and sets it as an environment variable.
    This makes the backend compliant with the frontend's expected behavior.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    if not api_key:
        raise HTTPException(status_code=401, detail="API key is missing")

    # Set the environment variable for the agno library to use for this request's context
    os.environ['OPENAI_API_KEY'] = api_key
    return api_key

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str

class NewsItem(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    url: str
    timestamp: datetime
    sentiment: str
    relevance: float
    tags: List[str]
    coins: List[str]
    agentId: str

# ... (Other Pydantic models are the same)
class Trade(BaseModel):
    id: str
    token: str
    action: str
    amount: float
    price: float
    timestamp: datetime
    profit: float
    status: str

class AgentActivity(BaseModel):
    id: str
    timestamp: datetime
    type: str
    message: str
    details: Dict[str, Any]

class PriceDataPoint(BaseModel):
    time: float
    price: float

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "CryptoSentinel API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/status")
async def get_status(api_key: str = Depends(get_api_key)):
    return {"status": "connected", "message": "Authenticated successfully"}

# --- Helper for Agent API Calls with Retries ---
def run_agent_with_retry(prompt: str, max_retries: int = 3):
    """
    Runs an agent prompt, rotating API keys on failure.
    """
    # The number of keys provides a natural limit for retries.
    num_keys = len(key_manager.api_keys)
    for i in range(min(max_retries, num_keys)):
        try:
            # Set the current key for the model to use
            crypto_trading_team.model.api_key = key_manager.get_key()

            response = crypto_trading_team.run(prompt, stream=False)
            return str(response)
        except Exception as e:
            print(f"Agent call failed with key index {key_manager.current_key_index}. Error: {e}")
            # Check if it's a key-related error (this is a heuristic)
            if "api key" in str(e).lower() or "resource has been exhausted" in str(e).lower():
                key_manager.rotate_key()
                print("Retrying with new key...")
            else:
                # For other errors, don't retry, just raise
                raise e
    raise Exception("Agent call failed after multiple retries with different keys.")


# --- Core Data Endpoints ---
@app.get("/news/latest", response_model=List[NewsItem])
async def get_latest_news(limit: int = 20, api_key: str = Depends(get_api_key)):
    """
    Fetches the latest cryptocurrency news using DuckDuckGo search.
    """
    try:
        # Use DuckDuckGo news tool directly for reliability
        ddg_news = DuckDuckGoTools(news=True)
        news_results = ddg_news.duckduckgo_news(query="cryptocurrency")

        # The tool does not support a limit, so we slice the results
        if isinstance(news_results, list):
            news_results = news_results[:limit]

        # The output of the tool is a string, so we need to parse it.
        # This is a bit brittle, but it's how the tool is designed.
        # A better implementation would have the tool return structured data.
        if isinstance(news_results, str):
            try:
                # The string is a JSON representation of a list of dicts
                news_items_raw = json.loads(news_results)
            except json.JSONDecodeError:
                print(f"Failed to parse news results from DDG: {news_results}")
                return []
        else:
            # If it's already a list (which it should be), use it directly
            news_items_raw = news_results

        # Format the results into the NewsItem model
        formatted_news = []
        for i, item in enumerate(news_items_raw):
            # The news tool returns 'date', 'title', 'body', 'url', 'source'
            # We need to map this to our NewsItem model
            formatted_news.append(
                NewsItem(
                    id=f"news_{int(datetime.now().timestamp())}_{i}",
                    title=item.get("title", "No Title"),
                    summary=item.get("body", ""),
                    source=item.get("source", "Unknown Source"),
                    url=item.get("url", "#"),
                    timestamp=datetime.fromisoformat(item.get("date")) if item.get("date") else datetime.now(),
                    sentiment="neutral",  # Sentiment analysis would require another agent/tool
                    relevance=0.8,  # Relevance scoring would require another agent/tool
                    tags=["crypto"],
                    coins=[],  # Coin extraction would require another agent/tool
                    agentId="DuckDuckGoTools",
                )
            )
        return formatted_news
    except Exception as e:
        print(f"Failed to fetch news from DuckDuckGo: {e}")
        return []

@app.get("/trades/recent", response_model=List[Trade])
async def get_recent_trades(limit: int = 15, api_key: str = Depends(get_api_key)):
    """Returns the most recent trades from the in-memory database."""
    return db_get_recent_trades(limit)

@app.get("/agent/activities/recent", response_model=List[AgentActivity])
async def get_recent_agent_activities(limit: int = 20, api_key: str = Depends(get_api_key)):
    """Returns the most recent agent activities from the in-memory database."""
    return db_get_recent_activities(limit)

@app.get("/market/price", response_model=List[PriceDataPoint])
async def get_market_price(symbol: str = "BTC", period: str = "1D", api_key: str = Depends(get_api_key)):
    """
    Fetches real market price data directly from the CoinGecko API.
    """
    # Mapping for symbols to CoinGecko IDs
    symbol_to_id = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "DOGE": "dogecoin",
        # Add other common symbols here
    }
    coin_id = symbol_to_id.get(symbol.upper(), symbol.lower())

    # Mapping for period to days
    period_to_days = {
        "1D": 1,
        "7D": 7,
        "1M": 30,
        "3M": 90,
        "1Y": 365,
    }
    days = period_to_days.get(period.upper(), 1)

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Process the data into the format expected by the frontend
        price_data = [
            PriceDataPoint(time=item[0] / 1000, price=item[1])
            for item in data.get("prices", [])
        ]
        return price_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from CoinGecko: {e}")
        return []
    except Exception as e:
        print(f"An error occurred while processing price data: {e}")
        return []

# --- Chat Endpoint ---
@app.post("/chat")
async def chat_with_agent(request: ChatRequest, api_key: str = Depends(get_api_key)):
    try:
        response_generator = crypto_trading_team.run(request.message, stream=True)

        async def stream_output():
            for chunk in response_generator:
                # The generator can yield strings or event objects.
                # We only want to stream the string responses to the client.
                if isinstance(chunk, str):
                    yield chunk
                else:
                    # For debugging, we can see the events happening
                    print(f"AGENT_EVENT: {chunk}")

        return StreamingResponse(stream_output(), media_type="text/event-stream")
    except Exception as e:
        print(f"Error during chat: {e}")
        async def error_stream():
            yield f"Error: Could not get response from agent. {e}"
        return StreamingResponse(error_stream(), media_type="text/event-stream", status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
