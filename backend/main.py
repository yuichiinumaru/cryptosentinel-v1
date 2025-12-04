import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from agno.tools.duckduckgo import DuckDuckGoTools
from backend.storage.models import TradeData, ActivityData
from backend.agents import crypto_trading_team, storage

# Configure Logging
logging.getLogger("uvicorn").setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="DeepTrader API - Resurrected")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
async def get_api_key(authorization: str = Header(None)) -> str:
    """
    Validates the Authorization header.
    SECURITY FIX: Does NOT inject into global os.environ.
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

    # In a production environment, we would verify this key against a database.
    # For now, strict validation is enough.
    return api_key


# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "DeepTrader API is running (Resurrected & Fortified)"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/status")
@limiter.limit("60/minute")
async def get_status(request: Request, api_key: str = Depends(get_api_key)):
    return {"status": "connected", "message": "Authenticated successfully"}


# --- Core Data Endpoints ---
@app.get("/news/latest", response_model=List[NewsItem])
@limiter.limit("10/minute")
async def get_latest_news(request: Request, limit: int = 20, api_key: str = Depends(get_api_key)):
    """
    Fetches the latest cryptocurrency news using DuckDuckGo search.
    Executes in a threadpool to prevent blocking the event loop.
    """
    try:
        def fetch_news():
            ddg_news = DuckDuckGoTools(news=True)
            return ddg_news.duckduckgo_news(query="cryptocurrency")

        news_results = await run_in_threadpool(fetch_news)

        if isinstance(news_results, list):
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
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/trades/recent", response_model=List[TradeData])
@limiter.limit("30/minute")
async def get_recent_trades(request: Request, limit: int = 15, api_key: str = Depends(get_api_key)):
    """Returns the most recent trades from the database (Non-blocking)."""
    return await run_in_threadpool(storage.get_recent_trades, limit)

@app.get("/agent/activities/recent", response_model=List[ActivityData])
@limiter.limit("30/minute")
async def get_recent_agent_activities(request: Request, limit: int = 20, api_key: str = Depends(get_api_key)):
    """Returns the most recent agent activities from the database (Non-blocking)."""
    return await run_in_threadpool(storage.get_recent_activities, limit)

@app.get("/market/price", response_model=List[PriceDataPoint])
@limiter.limit("20/minute")
async def get_market_price(request: Request, symbol: str = "BTC", period: str = "1D", api_key: str = Depends(get_api_key)):
    """
    Fetches real market price data directly from the CoinGecko API.
    """
    # Helper to map symbols. In a real system, this would be a DB lookup or config.
    def get_coin_id(sym: str) -> str:
        mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "DOGE": "dogecoin",
            "SOL": "solana",
            "MATIC": "matic-network",
            "BNB": "binancecoin",
        }
        return mapping.get(sym.upper(), sym.lower())

    coin_id = get_coin_id(symbol)

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

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Coin '{symbol}' not found")
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
@limiter.limit("10/minute")
async def chat_with_agent(request: Request, chat_req: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    Handles chat requests to the agency.
    Executes the agent run loop in a separate thread to prevent blocking.
    """
    try:
        def run_agent_sync(msg: str):
            # This is a blocking CPU/IO bound operation
            return crypto_trading_team.run(msg)

        run_output = await run_in_threadpool(run_agent_sync, chat_req.message)

        final_response = ""
        if hasattr(run_output, "get_content_as_string"):
            final_response = run_output.get_content_as_string() or ""
            if not final_response and getattr(run_output, "content", None):
                final_response = str(run_output.content)
        elif isinstance(run_output, str):
            final_response = run_output
        else:
            try:
                # Handle iterator output if any (exhaust it)
                for chunk in run_output:
                    if isinstance(chunk, dict) and "content" in chunk:
                        final_response += str(chunk["content"])
                    elif isinstance(chunk, str):
                        final_response += chunk
            except TypeError:
                final_response = str(run_output)

        if not final_response:
            final_response = "The agent performed an action but returned no verbal response."

        return {"response": final_response}

    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
