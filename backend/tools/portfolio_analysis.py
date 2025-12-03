import os
from typing import Dict, Any

import numpy as np
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class CalculatePortfolioMetricsOutput(BaseModel):
    roi: float = Field(..., description="Return on investment.")
    pnl: float = Field(..., description="Profit and loss in USD.")
    max_drawdown: float = Field(..., description="Maximum historical drawdown.")


def calculate_portfolio_metrics() -> CalculatePortfolioMetricsOutput:
    storage = _get_storage()
    positions = storage.get_portfolio_positions()
    trades = storage.get_recent_trades(limit=500)

    total_value = sum((pos.last_valuation_usd or pos.amount * pos.average_price) for pos in positions)
    cost_basis = sum(pos.average_price * pos.amount for pos in positions)
    pnl = total_value - cost_basis
    roi = pnl / cost_basis if cost_basis else 0.0

    equity_curve = []
    cumulative = 0.0
    for trade in trades:
        cumulative += getattr(trade, "profit", 0.0)
        equity_curve.append(cumulative)
    if equity_curve:
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdowns = equity_array - running_max
        max_drawdown = float(drawdowns.min())
    else:
        max_drawdown = 0.0

    return CalculatePortfolioMetricsOutput(roi=roi, pnl=pnl, max_drawdown=max_drawdown)

class CalculatePortfolioRiskInput(BaseModel):
    pass

class CalculatePortfolioRiskOutput(BaseModel):
    volatility: float = Field(..., description="Portfolio profit volatility.")
    var: float = Field(..., description="Value at Risk (5% percentile).")
    exposure: Dict[str, float] = Field(..., description="Per-asset exposure weights.")


def calculate_portfolio_risk() -> CalculatePortfolioRiskOutput:
    storage = _get_storage()
    positions = storage.get_portfolio_positions()
    trades = storage.get_recent_trades(limit=300)

    profits = np.array([getattr(trade, "profit", 0.0) for trade in trades])
    volatility = float(np.std(profits)) if profits.size else 0.0
    var = float(np.percentile(profits, 5)) if profits.size else 0.0

    total_value = sum((pos.last_valuation_usd or pos.amount * pos.average_price) for pos in positions)
    exposure: Dict[str, float] = {}
    for pos in positions:
        value = pos.last_valuation_usd or pos.amount * pos.average_price
        exposure[pos.symbol] = value / total_value if total_value else 0.0

    return CalculatePortfolioRiskOutput(volatility=volatility, var=var, exposure=exposure)


portfolio_analysis_toolkit = Toolkit(name="portfolio_analysis")
portfolio_analysis_toolkit.register(calculate_portfolio_metrics)
portfolio_analysis_toolkit.register(calculate_portfolio_risk)
class PortfolioAnalysisToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="portfolio_analysis", tools=[
            self.calculate_portfolio_metrics,
            self.calculate_portfolio_risk,
        ], **kwargs)

    def calculate_portfolio_metrics(self) -> CalculatePortfolioMetricsOutput:
        """
        Calculates portfolio performance metrics.
        """
        # ... (Placeholder implementation)
        return CalculatePortfolioMetricsOutput(roi=0.1, pnl=1000, max_drawdown=0.05)

    def calculate_portfolio_risk(self) -> CalculatePortfolioRiskOutput:
        """
        Calculates portfolio risk metrics.
        """
        # ... (Placeholder implementation)
        return CalculatePortfolioRiskOutput(volatility=0.2, var=100, exposure={"BTC": 0.5, "ETH": 0.5})

portfolio_analysis_toolkit = PortfolioAnalysisToolkit()
