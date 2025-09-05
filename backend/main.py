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

# --- Mock Data Generation (only for news fallback) ---
def create_mock_news(limit: int) -> List[NewsItem]:
    items = []
    for i in range(limit):
        items.append(NewsItem(id=f"news_{i}", title=f"Breaking News on Crypto {i}", summary="A detailed summary...", source="Crypto News Today", url="https://example.com/news", timestamp=datetime.now() - timedelta(hours=i), sentiment=random.choice(["positive", "negative", "neutral"]), relevance=random.random(), tags=["DeFi"], coins=["BTC"], agentId="MarketAnalyst_01"))
    return items

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
async def get_latest_news(limit: int = 5, api_key: str = Depends(get_api_key)):
    prompt = f"""
    Find the {limit} latest news articles about cryptocurrency.
    Format the output as a valid JSON list of objects.
    Each object must have these keys: id, title, summary, source, url, timestamp, sentiment, relevance, tags, coins, agentId.
    Your final output should be ONLY the JSON list, with no other text or formatting.
    """
    try:
        response_str = run_agent_with_retry(prompt)
        news_data = json.loads(response_str)
        return [NewsItem(**item) for item in news_data]
    except Exception as e:
        print(f"Agent failed to generate news, falling back to mock data. Error: {e}")
        return create_mock_news(limit)

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
