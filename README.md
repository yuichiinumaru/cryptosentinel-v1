
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
- **OpenAI Integration**: Use your own API key and optionally a custom endpoint

## API Integration

### Backend Connection Setup

CryptoSentinel is designed to work with a Python backend API that handles the actual data processing, trading logic, and AI operations. The frontend is a React application that communicates with this backend through a REST API.

#### API Configuration

1. **Setting Up the Connection**:
   - Navigate to the Settings tab in the dashboard
   - In the API Configuration section, enter your backend API URL (default is http://localhost:5000)
   - Click "Test" to verify the connection
   - Provide your OpenAI API key for the AI agents functionality
   - Optionally, enter a custom OpenAI endpoint if you're using an alternative service
   - Click "Save API Configuration" to store these settings

2. **API Storage**:
   - The API URL is stored in localStorage as "apiUrl"
   - The OpenAI API key is stored in localStorage as "openaiApiKey"
   - The custom OpenAI endpoint (if provided) is stored in localStorage as "openaiEndpoint"

### Backend API Structure

The frontend expects the following API endpoints to be available on your Python backend:

#### Health & Status
- `GET /health`: Simple endpoint to check if the API is running
- `GET /status`: Get the current status of the system

#### News Endpoints
- `GET /news`: Get all stored news items
- `GET /news/latest?limit={limit}`: Get the latest news items, limited by the specified number
- `GET /news/tags/{tag}`: Get news items filtered by specific tag
- `GET /news/sentiment/{sentiment}`: Get news items filtered by sentiment (positive/negative/neutral)

#### Trade Endpoints
- `GET /trades`: Get all trade history
- `GET /trades/recent?limit={limit}`: Get recent trades, limited by the specified number
- `POST /trades/execute`: Execute a new trade (requires trade data in the request body)

#### Agent Activity Endpoints
- `GET /agent/activities`: Get all agent activities
- `GET /agent/activities/type/{type}`: Get activities filtered by type
- `GET /agent/activities/recent?limit={limit}`: Get recent agent activities

#### AI Learning System Endpoints
- `GET /ai/learnings`: Get insights from the AI learning system
- `GET /ai/knowledge`: Get the current AI knowledge database
- `POST /ai/train`: Trigger AI model training

#### Market Data Endpoints
- `GET /market/price?symbol={symbol}&period={period}`: Get price data for a specific symbol and time period
- `GET /market/price/current?symbol={symbol}`: Get the current price of a specific symbol

#### Configuration Endpoints
- `GET /config`: Get the current system configuration
- `POST /config`: Update the system configuration
- `POST /config/openai`: Update OpenAI-specific configuration

### Authentication

The frontend sends the OpenAI API key in the Authorization header for all requests:

```
Authorization: Bearer {openaiApiKey}
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

5. **OpenAI Integration**: The backend should use the provided OpenAI API key to power the AI agents, either directly or through a service like LangChain.

6. **State Management**: The backend should maintain state for the agent system, trading history, and configuration.

### Example Python Backend Skeleton

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="CryptoSentinel API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="API key is required")
    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return api_key
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

# Health endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# News endpoints
@app.get("/news/latest")
async def get_latest_news(limit: int = 20, api_key: str = Depends(get_api_key)):
    # Implement news retrieval logic
    return []  # Return list of news items

# Trade endpoints
@app.get("/trades/recent")
async def get_recent_trades(limit: int = 10, api_key: str = Depends(get_api_key)):
    # Implement trade retrieval logic
    return []  # Return list of trades

# Agent activity endpoints
@app.get("/agent/activities/recent")
async def get_recent_activities(limit: int = 20, api_key: str = Depends(get_api_key)):
    # Implement activity retrieval logic
    return []  # Return list of activities

# Main execution point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

## Project Status

This project is under active development. The frontend is complete and ready to connect to your Python backend.
