from typing import Dict, Any
import pandas as pd
import numpy as np
import httpx
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from backend.tools.utils import fetch_coingecko_prices

class GetQuantMetricsInput(BaseModel):
    symbol: str = Field(..., description="The CoinGecko ID of the token.")
    days: int = Field(365, description="Analysis period (default 1 year).")
    risk_free_rate: float = Field(0.02, description="Risk-free rate (default 2%).")

class QuantitativeAnalysisToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="quant_analysis", **kwargs)
        self.register(self.get_quant_metrics)

    async def get_quant_metrics(self, input: GetQuantMetricsInput) -> Dict[str, Any]:
        """
        Calculates advanced risk metrics (Sharpe, Sortino, VaR, Max Drawdown).
        """
        symbol = input.symbol
        days = input.days
        rf = input.risk_free_rate

        try:
            async with httpx.AsyncClient() as client:
                try:
                    df = await fetch_coingecko_prices(client, symbol, days)
                except Exception as e:
                    return {"error": f"Failed to fetch data: {e}"}

            if len(df) < 2:
                return {"error": "Insufficient data"}

            prices = df["price"]

            # Returns
            returns = prices.pct_change().dropna()
            mean_return = returns.mean() * 365  # Annualized
            std_dev = returns.std() * np.sqrt(365) # Annualized

            # Metrics

            # Sharpe Ratio
            if std_dev == 0:
                sharpe = 0.0
            else:
                sharpe = (mean_return - rf) / std_dev

            # Sortino Ratio
            downside_returns = returns[returns < 0]
            if len(downside_returns) == 0:
                sortino = 0.0
            else:
                downside_std = downside_returns.std() * np.sqrt(365)
                sortino = (mean_return - rf) / downside_std

            # Value at Risk (Historical 95%)
            var_95 = np.percentile(returns, 5) # 5th percentile of daily returns

            # Max Drawdown
            cumulative = (1 + returns).cumprod()
            peak = cumulative.cummax()
            drawdown = (cumulative - peak) / peak
            max_drawdown = drawdown.min()

            return {
                "sharpe_ratio": float(sharpe),
                "sortino_ratio": float(sortino),
                "var_95_daily": float(var_95),
                "max_drawdown": float(max_drawdown),
                "annualized_volatility": float(std_dev)
            }

        except Exception as e:
            return {"error": str(e)}
