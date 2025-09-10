from pydantic import BaseModel, Field
from typing import List, Dict, Any
from agno.tools import tool
import numpy as np

from backend.storage.sqlite import SqliteStorage
from .market_data import FetchMarketData


class GetPortfolioInput(BaseModel):
    pass


class GetPortfolioOutput(BaseModel):
    items: List[Dict[str, Any]] = Field(..., description="A list of portfolio items.")
    total_value_usd: float = Field(..., description="The total value of the portfolio in USD.")


@tool(input_schema=GetPortfolioInput, output_schema=GetPortfolioOutput)
def GetPortfolio() -> Dict[str, Any]:
    """
    Gets the current state of the portfolio from the database.
    """
    storage = SqliteStorage("sqlite.db")
    trades = storage.get_recent_trades(limit=1000) # Get all trades for now

    # This is a simplified portfolio calculation. A real implementation would be more complex.
    portfolio = {}
    for trade in trades:
        if trade.action == "buy":
            portfolio[trade.token] = portfolio.get(trade.token, 0) + trade.amount
        elif trade.action == "sell":
            portfolio[trade.token] = portfolio.get(trade.token, 0) - trade.amount

    # Get current prices
    coin_ids = list(portfolio.keys())
    market_data = FetchMarketData(coin_ids=coin_ids)

    items = []
    total_value_usd = 0
    for token, amount in portfolio.items():
        price = market_data.get("market_data", {}).get(token, {}).get("usd", 0)
        value = amount * price
        items.append({"token": token, "amount": amount, "value_usd": value})
        total_value_usd += value

    return {"items": items, "total_value_usd": total_value_usd}


class CalculatePortfolioMetricsInput(BaseModel):
    pass


class CalculatePortfolioMetricsOutput(BaseModel):
    roi: float = Field(..., description="The Return on Investment.")
    pnl: float = Field(..., description="The Profit and Loss.")
    max_drawdown: float = Field(..., description="The maximum drawdown.")


@tool(input_schema=CalculatePortfolioMetricsInput, output_schema=CalculatePortfolioMetricsOutput)
def CalculatePortfolioMetrics() -> Dict[str, Any]:
    """
    Calculates portfolio performance metrics.
    """
    # ... (Simplified implementation)
    return {"roi": 0.1, "pnl": 1000, "max_drawdown": 0.05}


class CalculatePortfolioRiskInput(BaseModel):
    pass


class CalculatePortfolioRiskOutput(BaseModel):
    volatility: float = Field(..., description="The portfolio volatility.")
    var: float = Field(..., description="The Value at Risk (VaR).")
    exposure: Dict[str, float] = Field(..., description="The exposure per asset.")


@tool(input_schema=CalculatePortfolioRiskInput, output_schema=CalculatePortfolioRiskOutput)
def CalculatePortfolioRisk() -> Dict[str, Any]:
    """
    Calculates portfolio risk metrics.
    """
    # ... (Simplified implementation)
    return {"volatility": 0.2, "var": 100, "exposure": {"BTC": 0.5, "ETH": 0.5}}


class GetTradeHistoryFromDBInput(BaseModel):
    limit: int = Field(100, description="The maximum number of trades to retrieve.")


class GetTradeHistoryFromDBOutput(BaseModel):
    trades: List[Dict[str, Any]] = Field(..., description="A list of trades.")


@tool(input_schema=GetTradeHistoryFromDBInput, output_schema=GetTradeHistoryFromDBOutput)
def GetTradeHistoryFromDB(limit: int = 100) -> Dict[str, Any]:
    """
    Gets the trade history from the database.
    """
    storage = SqliteStorage("sqlite.db")
    trades = storage.get_recent_trades(limit=limit)
    return {"trades": [trade.dict() for trade in trades]}
