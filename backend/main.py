import os
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any
from datetime import datetime
import json
import requests
from fastapi.responses import StreamingResponse

from backend.storage.models import TradeData, ActivityData
from backend.agents import crypto_trading_team, storage


app = FastAPI(title="DeepTrader API")

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
    agent: str = "DeepTraderManager"  # Default agent to chat with

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


# The crypto_trading_team is already instantiated in backend/agents.py
# We just use it here.


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
    os.environ['GEMINI_API_KEY'] = api_key
    return api_key


# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "DeepTrader API is running"}

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
    Fetches the latest cryptocurrency news by asking the agent team.
    """
    try:
        # Ask the AnalistaDeSentimento to fetch the latest news.
        # The response should be a list of NewsItem objects.
        response = crypto_trading_team.run(
            f"Fetch the latest {limit} cryptocurrency news articles."
        )

        # The response from the team might be a generator, so we consume it.
        # The final result should be a JSON string representing a list of news items.
        final_response = ""
        for chunk in response:
            if isinstance(chunk, dict) and 'content' in chunk:
                final_response += chunk['content']
            elif isinstance(chunk, str):
                final_response = chunk

        if not final_response:
            return []

        # The agent should return a JSON string that we can parse into our model.
        news_items_raw = json.loads(final_response)

        # Validate and format the response
        formatted_news = [NewsItem(**item) for item in news_items_raw]
        return formatted_news

    except Exception as e:
        print(f"Error fetching news from agent team: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news from agent team.")

@app.get("/trades/recent", response_model=List[TradeData])
async def get_recent_trades(limit: int = 15, api_key: str = Depends(get_api_key)):
    """Returns the most recent trades from the database."""
    return storage.get_recent_trades(limit)

@app.get("/agent/activities/recent", response_model=List[ActivityData])
async def get_recent_agent_activities(limit: int = 20, api_key: str = Depends(get_api_key)):
    """Returns the most recent agent activities from the database."""
    return storage.get_recent_activities(limit)

@app.get("/market/price", response_model=List[PriceDataPoint])
async def get_market_price(symbol: str = "BTC", period: str = "1D", api_key: str = Depends(get_api_key)):
    """
    Fetches market price data by asking the MarketAnalyst agent.
    """
    try:
        # Ask the MarketAnalyst to fetch the price data.
        response = crypto_trading_team.run(
            f"Fetch the market price for {symbol} for the last {period}."
        )

        # The response from the team might be a generator, so we consume it.
        final_response = ""
        for chunk in response:
            if isinstance(chunk, dict) and 'content' in chunk:
                final_response += chunk['content']
            elif isinstance(chunk, str):
                final_response = chunk

        if not final_response:
            return []

        # The agent should return a JSON string that we can parse into our model.
        price_data_raw = json.loads(final_response)

        # Validate and format the response
        price_data = [PriceDataPoint(**item) for item in price_data_raw]
        return price_data

    except Exception as e:
        print(f"Error fetching market price from agent team: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market price from agent team.")


@app.post("/chat")
async def chat_with_agent(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    Handles chat requests to the agency. The user can specify which agent to talk to.
    The message is sent from a "User" sender to the specified agent.
    """
    try:
        # Use the team to get a response.
        # The 'team' object from agno might have a different interface.
        # Based on the library's likely design, it probably takes the message
        # and determines the initial agent based on its internal logic or a default.
        # The concept of a specific 'receiver' might be handled differently in a Team.
        # For now, let's assume a simple run method. I may need to adjust this
        # after checking the agno library's source or getting more errors.
        response_generator = crypto_trading_team.run(request.message, stream=True)

        # The `run` method of a team with stream=True returns a generator.
        # We need to iterate through it to get the final content.
        final_response = ""
        for chunk in response_generator:
            # The chunk can be a string or a dictionary-like object (event).
            # We are interested in the string content.
            if isinstance(chunk, str):
                final_response += chunk
            elif hasattr(chunk, 'content') and isinstance(chunk.content, str):
                 final_response += chunk.content


        # If the agent returns a structured object (like a Pydantic model),
        # agno will serialize it to a string. We might need to parse it back
        # depending on the frontend's needs. For now, we return the raw response.
        if not final_response:
             final_response = "The agent did not return a message. This could be because it performed an action without a verbal response."

        return {"response": final_response}

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # This will catch errors like agent not found, etc.
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
