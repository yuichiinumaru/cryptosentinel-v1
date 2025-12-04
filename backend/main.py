import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from agno.tools.duckduckgo import DuckDuckGoTools
from backend.storage.models import TradeData, ActivityData
from backend.agents import crypto_trading_team, storage

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DeepTrader API - Resurrected")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str
    agent: str = "DeepTraderManager"

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

class PriceDataPoint(BaseModel):
    time: float
    price: float

# --- Authentication Dependency ---
async def get_api_key(authorization: str = Header(None)):
    """
    Validates the Authorization header.
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

    # In a real resurrection, we would validate this key against a vault/DB
    # For now, we strictly ensure it is passed to the environment context
    os.environ['OPENAI_API_KEY'] = api_key
    return api_key


# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "DeepTrader API is running (Resurrected)"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/status")
async def get_status(api_key: str = Depends(get_api_key)):
    return {"status": "connected", "message": "Authenticated successfully"}


# --- Core Data Endpoints ---
@app.get("/news/latest", response_model=List[NewsItem])
async def get_latest_news(limit: int = 20, api_key: str = Depends(get_api_key)):
    """
    Fetches the latest cryptocurrency news using DuckDuckGo search.
    """
    try:
        ddg_news = DuckDuckGoTools(news=True)
        # DuckDuckGoTools is synchronous. Ideally, run in threadpool.
        # But for now, we wrap the output handling.
        news_results = ddg_news.duckduckgo_news(query="cryptocurrency")

        if isinstance(news_results, list):
            # If tool returns list, use it directly (it might be list of dicts)
            news_items_raw = news_results
        elif isinstance(news_results, str):
            try:
                news_items_raw = json.loads(news_results)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse news results: {e}")
                raise HTTPException(status_code=502, detail="Upstream news provider returned invalid data")
        else:
            logger.error(f"Unexpected news result type: {type(news_results)}")
            return []

        # Slice limits
        news_items_raw = news_items_raw[:limit]

        formatted_news = []
        for i, item in enumerate(news_items_raw):
            formatted_news.append(
                NewsItem(
                    id=f"news_{int(datetime.now().timestamp())}_{i}",
                    title=item.get("title", "No Title"),
                    summary=item.get("body", ""),
                    source=item.get("source", "Unknown Source"),
                    url=item.get("url", "#"),
                    timestamp=datetime.fromisoformat(item.get("date")) if item.get("date") else datetime.now(),
                    sentiment="neutral",
                    relevance=0.8,
                    tags=["crypto"],
                    coins=[],
                    agentId="DuckDuckGoTools",
                )
            )
        return formatted_news
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch news")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trades/recent", response_model=List[TradeData])
async def get_recent_trades(limit: int = 15, api_key: str = Depends(get_api_key)):
    """Returns the most recent trades from the database."""
    # storage calls are sync, implying blocking. In real resurrection, convert storage to async.
    # For now, we accept this legacy sin until storage layer rewrite.
    return storage.get_recent_trades(limit)

@app.get("/agent/activities/recent", response_model=List[ActivityData])
async def get_recent_agent_activities(limit: int = 20, api_key: str = Depends(get_api_key)):
    """Returns the most recent agent activities from the database."""
    return storage.get_recent_activities(limit)

@app.get("/market/price", response_model=List[PriceDataPoint])
async def get_market_price(symbol: str = "BTC", period: str = "1D", api_key: str = Depends(get_api_key)):
    """
    Fetches real market price data directly from the CoinGecko API using AsyncClient.
    """
    symbol_to_id = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "DOGE": "dogecoin",
    }
    coin_id = symbol_to_id.get(symbol.upper(), symbol.lower())

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

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            price_data = [
                PriceDataPoint(time=item[0] / 1000, price=item[1])
                for item in data.get("prices", [])
            ]
            return price_data
        except httpx.HTTPStatusError as e:
            logger.error(f"CoinGecko API error: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Market data provider error")
        except httpx.RequestError as e:
            logger.error(f"CoinGecko connection error: {e}")
            raise HTTPException(status_code=503, detail="Market data provider unavailable")
        except Exception as e:
            logger.exception("Unexpected error processing price data")
            raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/chat")
async def chat_with_agent(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    Handles chat requests to the agency.
    REMOVED: Mock logic. This now runs the actual agent.
    """
    try:
        # In a real async system, crypto_trading_team.run would be async.
        # Since agno is sync, we should offload this to a thread if possible,
        # or accept the block. Given "Fail Loudly", we will run it and catch errors.

        # NOTE: crypto_trading_team.run might block!
        run_output = crypto_trading_team.run(request.message)

        final_response = ""
        if hasattr(run_output, "get_content_as_string"):
            final_response = run_output.get_content_as_string() or ""
            if not final_response and getattr(run_output, "content", None):
                final_response = str(run_output.content)
        elif isinstance(run_output, str):
            final_response = run_output
        else:
            try:
                # Handle iterator output if any
                for chunk in run_output:
                    if isinstance(chunk, dict) and "content" in chunk:
                        final_response += str(chunk["content"])
                    elif isinstance(chunk, str):
                        final_response += chunk
            except TypeError:
                # If it's not iterable, convert to str
                final_response = str(run_output)

        if not final_response:
            final_response = "The agent performed an action but returned no verbal response."

        return {"response": final_response}

    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
