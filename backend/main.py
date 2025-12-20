import asyncio
import os
import json
import logging
import secrets
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache

import httpx
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from agno.tools.duckduckgo import DuckDuckGoTools
from backend.storage.models import TradeData, ActivityData
from backend.agents import get_crypto_trading_team, storage
from backend.tools.consensus import ConsensusToolkit

# Configure Logging
log_level_env = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level_env.upper(), logging.INFO))
logger = logging.getLogger(__name__)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="DeepTrader API - Resurrected & Purified")
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

# --- Authentication & Security ---
class SecurityConfig:
    """
    Immutable security configuration.
    Guards against empty or weak secrets.
    """
    def __init__(self):
        self._api_key = os.getenv("API_KEY")

        # Rite 5: Security Hardening
        # Fail immediately if API Key is insecure. Zero Trust.
        if not self._api_key or self._api_key == "CHANGE_ME_IN_PROD_PLEASE":
            raise RuntimeError("CRITICAL: API_KEY is missing or default. Please set a secure API_KEY in .env.")

    def validate(self, input_key: str) -> bool:
        if not self._api_key:
             return False
        return secrets.compare_digest(self._api_key, input_key)

@lru_cache()
def get_security_config() -> SecurityConfig:
    return SecurityConfig()

async def get_api_key(
    authorization: str = Header(..., description="Bearer <API_KEY>"),
    config: SecurityConfig = Depends(get_security_config)
) -> str:
    """
    Verifies the Authorization header using constant-time comparison.
    Returns the raw API Key.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    if not config.validate(token):
        logger.warning(f"Failed auth attempt.")
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return token

def get_session_id(api_key: str) -> str:
    """Derives a deterministic session ID from the API Key."""
    return hashlib.sha256(api_key.encode()).hexdigest()

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
            # Note: This is still potentially blocking IO in a thread.
            # Ideally migrate to async search client.
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
    Uses API Key if available.
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

    # CoinGecko Auth Injection
    cg_api_key = os.getenv("COINGECKO_API_KEY")

    params = {
        "vs_currency": "usd",
        "days": days,
    }

    headers = {}
    if cg_api_key:
         headers["x-cg-demo-api-key"] = cg_api_key

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
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
            if e.response.status_code == 429:
                 raise HTTPException(status_code=429, detail="Market data rate limit exceeded. Please configure COINGECKO_API_KEY.")
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
    Creates an isolated Team instance for the session.
    """
    try:
        session_id = get_session_id(api_key)

        # --- Sleep-Time Compute Phase ---
        # Before handling the user's request, run the MentalPreparation agent to prime the memory.
        # This is a non-blocking call that happens before the main logic.
        async def run_mental_prep():
            logger.info(f"[{session_id}] Initiating sleep-time compute phase...")
            team = get_crypto_trading_team(session_id)
            prep_agent = team.get_member("MentalPreparation")
            if prep_agent:
                # We run this in a threadpool because the agent's internal logic might be sync
                await run_in_threadpool(prep_agent.run, "Begin mental preparation for the upcoming session.")
                logger.info(f"[{session_id}] Sleep-time compute phase complete.")
            else:
                logger.warning(f"[{session_id}] MentalPreparation agent not found. Skipping sleep-time compute.")

        # Run the preparation task. We don't need to block the user for this.
        # For simplicity in this implementation, we'll run it quickly and await it.
        # In a more advanced system, this could be a background task.
        await run_mental_prep()
        # --- End Sleep-Time Compute Phase ---

        consensus_toolkit = ConsensusToolkit()

        # New Consensus Logic
        if "with consensus" in chat_req.message.lower():
            k = int(os.getenv("CONSENSUS_SAMPLES", "3"))

            async def run_market_analyst_concurrently(msg: str, sess_id: str):
                # This function is designed to be run concurrently.
                return await run_in_threadpool(run_market_analyst_sync, msg, sess_id)

            def run_market_analyst_sync(msg: str, sess_id: str) -> str:
                # This is the synchronous function that will be executed in the threadpool.
                team = get_crypto_trading_team(sess_id)
                market_analyst = team.get_member("MarketAnalyst")
                if not market_analyst:
                    # Raise an exception to be caught by the calling task
                    raise ValueError("MarketAnalyst agent not found in the team.")

                # The agent's run method might be blocking, so it's correctly wrapped.
                result = market_analyst.run(msg)

                # Ensure we return a simple string
                if hasattr(result, "get_content_as_string"):
                    return result.get_content_as_string() or ""
                return str(result)

            analysis_prompt = chat_req.message.lower().replace("with consensus", "").strip()

            # Create k concurrent tasks
            tasks = [run_market_analyst_concurrently(analysis_prompt, session_id) for _ in range(k)]

            try:
                # Execute tasks concurrently and gather results
                analyst_outputs = await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.exception("An error occurred during concurrent agent execution.")
                raise HTTPException(status_code=500, detail=f"Error during consensus generation: {e}")


            votes = []
            for output in analyst_outputs:
                if isinstance(output, Exception):
                    logger.error(f"One of the analyst agents failed: {output}")
                    votes.append("NEUTRAL") # Default to neutral on error
                    continue

                # A simple heuristic to extract the vote
                if "BULLISH" in output.upper():
                    votes.append("BULLISH")
                elif "BEARISH" in output.upper():
                    votes.append("BEARISH")
                else:
                    votes.append("NEUTRAL")

            consensus = consensus_toolkit.majority_vote(votes)

            # Now, feed the consensus to the manager
            manager_prompt = f"The MarketAnalyst team has reached a '{consensus}' consensus on the following topic: '{analysis_prompt}'. Please proceed with the next logical step."

            def run_manager_sync(msg: str, sess_id: str):
                team = get_crypto_trading_team(sess_id)
                manager = team.get_member("DeepTraderManager")
                if not manager:
                    return "Error: DeepTraderManager not found."
                return manager.run(msg)

            run_output = await run_in_threadpool(run_manager_sync, manager_prompt, session_id)

        else:
            # Original logic for non-consensus requests
            def run_agent_sync(msg: str, sess_id: str):
                team = get_crypto_trading_team(sess_id)
                return team.run(msg)

            run_output = await run_in_threadpool(run_agent_sync, chat_req.message, session_id)

        # Process final output (same as before)
        final_response = ""
        if hasattr(run_output, "get_content_as_string"):
            final_response = run_output.get_content_as_string() or ""
            if not final_response and getattr(run_output, "content", None):
                final_response = str(run_output.content)
        elif isinstance(run_output, str):
            final_response = run_output
        else:
            try:
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
