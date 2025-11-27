
# CryptoSentinel - Autonomous Cryptocurrency Trading Bot

## Overview

CryptoSentinel is an advanced autonomous trading bot for cryptocurrencies, designed to provide secure, efficient, and intelligent trading capabilities. The system utilizes a multi-agent AI framework to analyze market data, execute trades, and continuously learn and improve its strategies.

## Features

### Dashboard
The main dashboard provides a comprehensive overview of your trading activity, funds, agent activities, and market data:
- **Real-time status indicator** showing the connection status with the backend
- **Funds Dashboard** displaying portfolio value, asset distribution, and profit/loss metrics
- **Agent Activity Monitor** showing real-time actions taken by the AI agents
- **Price Chart** with customizable timeframes and technical indicators
- **Recent Trades** list showing executed trades with their status and performance

### Trading System
- **Autonomous Trading**: The system executes trades automatically based on market analysis and your configured strategies
- **Manual Trading Controls**: Override capabilities for manual trades when needed
- **Trade History**: Complete log of all trades with performance metrics
- **Position Management**: Active position monitoring with stop-loss and take-profit settings

### Multi-Agent AI System
CryptoSentinel uses a team-based approach with multiple specialized AI agents:

1. **MarketAnalyst**: 
   - Analyzes market data and trends
   - Checks token security and identifies risks
   - Monitors news and social sentiment
   - Provides trading recommendations
   - Detects malicious market activity

2. **Trader**: 
   - Executes buy and sell orders
   - Manages the portfolio allocation
   - Implements trading strategies
   - Seeks arbitrage opportunities
   - Optimizes entry and exit points

3. **LearningManager**: 
   - Analyzes system performance
   - Adjusts strategies based on historical results
   - Maintains a knowledge database
   - Identifies patterns in successful/unsuccessful trades
   - Continuously improves agent instructions

4. **Manager**: 
   - Coordinates the agent team
   - Sets goals and objectives
   - Monitors overall performance
   - Assesses and manages risk
   - Makes high-level decisions

### Security Measures
- **MEV Protection**: Uses Flashbots Protect RPC to prevent sandwich attacks
- **Rug Pull Detection**: Analyzes contract code and liquidity to detect potential scams
- **Fake Volume Detection**: Identifies wash trading and market manipulation
- **Fund Isolation**: Separates funds into hot/cold wallets for enhanced security
- **Blacklist Management**: Custom blacklist for known malicious tokens and contracts

### Technical Analysis
- **Multiple Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, and more
- **Custom Strategy Builder**: Create and backtest your own strategies
- **Pattern Recognition**: Detects chart patterns like head and shoulders, triangles, etc.
- **Alert System**: Get notifications when specific conditions are met

### News Analysis
- **AI-powered News Filtering**: Automatically identifies relevant news for your portfolio
- **Sentiment Analysis**: Categorizes news as positive, negative, or neutral
- **Impact Assessment**: Measures potential market impact of news events
- **Ticker Bar**: Real-time scrolling news with sentiment indicators

### AI Learning System
- **Knowledge Database**: Growing collection of trading insights
- **Performance Analytics**: Historical analysis of strategy performance
- **Continuous Improvement**: System becomes more effective over time
- **Custom Training**: Ability to train on specific market conditions

### Customization
- **Multiple Themes**: 
  - Light Mode: Clean, professional interface for daytime use
  - Military Tactical Dark: Dark theme with a tactical, military aesthetic
  - Dark Grey: Neutral dark theme with low contrast 
  - Mr. Robot: Hacker-inspired theme with terminal aesthetics, glitch effects, and red accents
- **Configurable API**: Connect to your own backend with custom settings
- **Google Integration**: Use your own API key and optionally a custom endpoint

## API Integration

### Backend Connection Setup

CryptoSentinel is designed to work with a Python backend API that handles the actual data processing, trading logic, and AI operations. The frontend is a React application that communicates with this backend through a REST API.

#### API Configuration

1. **Setting Up the Connection**:
   - Navigate to the Settings tab in the dashboard
   - In the API Configuration section, enter your backend API URL (default is http://localhost:8000)
   - Click "Test" to verify the connection
   - Provide your Google API key for the AI agents functionality
   - Optionally, enter a custom Google endpoint if you're using an alternative service
   - Click "Save API Configuration" to store these settings

2. **API Storage**:
   - The API URL is stored in localStorage as "apiUrl"
   - The Google API key is stored in localStorage as "googleApiKey"
   - The custom Google endpoint (if provided) is stored in localStorage as "googleEndpoint"

### Backend API Structure

The frontend expects the following API endpoints to be available on your Python backend:

#### Health & Status
- `GET /health`: Simple endpoint to check if the API is running
- `GET /status`: Get the current status of the system

#### News Endpoints
- `GET /news`: Get all stored news items
- `GET /news/latest?limit={limit}`: Get the latest news items from DuckDuckGo News.

#### Trade Endpoints
- `GET /trades/recent?limit={limit}`: Get recent trades from the in-memory database, populated by the Trader agent.
- Other trade-related endpoints are available for more detailed history and execution.

#### Agent Activity Endpoints
- `GET /agent/activities/recent?limit={limit}`: Get recent agent activities from the in-memory database.

#### Market Data Endpoints
- `GET /market/price?symbol={symbol}&period={period}`: Get historical price data for a specific symbol and time period from CoinGecko.

#### Chat Endpoint
- `POST /chat`: A streaming endpoint to interact with the AI agent team.

#### Configuration Endpoints
- `GET /config`: Get the current system configuration.
- `POST /config`: Update the system configuration.

### Authentication

The frontend sends the Google API key in the Authorization header for all requests:

```
Authorization: Bearer {googleApiKey}
```

### Python Backend Implementation Guidelines

When implementing your Python backend, consider the following:

1. **Framework Recommendation**: FastAPI is recommended for implementing the backend API due to its performance and automatic OpenAPI documentation.

2. **CORS Configuration**: Ensure your backend has CORS properly configured to accept requests from your frontend domain.

3. **Data Structure**: Maintain consistent data structures as expected by the frontend:
   - News items should include: id, title, summary, source, url, timestamp, sentiment, relevance, tags, coins, agentId
   - Trades should include: id, token, action, amount, price, timestamp, profit, status
   - Agent activities should include: id, timestamp, type, message, details

4. **Error Handling**: Return appropriate HTTP status codes and error messages that the frontend can display to the user.

5. **Google Integration**: The backend should use the provided Google API key to power the AI agents, either directly or through a service like LangChain.

6. **State Management**: The backend should maintain state for the agent system, trading history, and configuration.

### Python Backend Implementation

The backend is a FastAPI application that uses the `agno` library for its multi-agent system. Here is a summary of the main implementation:

```python
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
from agno.tools.duckduckgo import DuckDuckGoTools

# --- Agent Team Import ---
from backend.agents import (
    crypto_trading_team,
    get_recent_trades as db_get_recent_trades,
    get_recent_activities as db_get_recent_activities,
    key_manager
)

app = FastAPI(title="CryptoSentinel API")

# Add CORS middleware
# ... (CORS configuration)

# --- Authentication & Pydantic Models ---
# ... (API key dependency and Pydantic models)

# --- API Endpoints ---

@app.get("/news/latest", response_model=List[NewsItem])
async def get_latest_news(limit: int = 20, api_key: str = Depends(get_api_key)):
    """
    Fetches the latest cryptocurrency news using DuckDuckGo search.
    """
    # ... (Implementation uses DuckDuckGoTools)

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
    # ... (Implementation uses requests to call CoinGecko)

@app.post("/chat")
async def chat_with_agent(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    Handles streaming chat with the AI agent team.
    """
    # ... (Implementation for streaming response)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

## Project Status

This project is fully functional. The frontend is complete and the backend provides live data for all main features.
