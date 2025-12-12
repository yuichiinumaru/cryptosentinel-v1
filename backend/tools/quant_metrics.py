from typing import Dict, Any, Optional, Union
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

    def _calc_cagr(self, prices: pd.Series) -> float:
        """Calculates Compound Annual Growth Rate."""
        if len(prices) < 2:
            return 0.0
        start_price = prices.iloc[0]
        end_price = prices.iloc[-1]
        years = len(prices) / 365.0
        if start_price == 0 or years == 0:
            return 0.0
        return float((end_price / start_price) ** (1 / years) - 1)

    def _calc_max_drawdown(self, prices: pd.Series) -> float:
        """Calculates Maximum Drawdown."""
        cumulative = (1 + prices.pct_change().dropna()).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return float(drawdown.min())

    def _calc_sharpe(self, returns: pd.Series, rf: float) -> float:
        """Calculates Sharpe Ratio."""
        if len(returns) < 2:
            return 0.0
        std_dev = returns.std() * np.sqrt(365)
        if std_dev == 0:
            return 0.0
        mean_return = returns.mean() * 365
        return float((mean_return - rf) / std_dev)

    def _calc_sortino(self, returns: pd.Series, rf: float) -> float:
        """Calculates Sortino Ratio."""
        downside_returns = returns[returns < 0]
        if len(downside_returns) < 2:
            return 0.0
        downside_std = downside_returns.std() * np.sqrt(365)
        if downside_std == 0:
            return 0.0
        mean_return = returns.mean() * 365
        return float((mean_return - rf) / downside_std)

    def _calc_calmar(self, cagr: float, max_dd: float) -> float:
        """Calculates Calmar Ratio."""
        if max_dd == 0:
            return 0.0
        return float(cagr / abs(max_dd))

    async def get_quant_metrics(self, input: GetQuantMetricsInput) -> Dict[str, Any]:
        """
        Calculates advanced risk metrics (Sharpe, Sortino, VaR, Max Drawdown, CAGR, Calmar).
        Inspired by 'ffn' library logic.
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
            returns = prices.pct_change().dropna()

            # Metric Calculations
            cagr = self._calc_cagr(prices)
            max_dd = self._calc_max_drawdown(prices)
            sharpe = self._calc_sharpe(returns, rf)
            sortino = self._calc_sortino(returns, rf)
            calmar = self._calc_calmar(cagr, max_dd)

            # Value at Risk (Historical 95%)
            var_95 = float(np.percentile(returns, 5))

            volatility = float(returns.std() * np.sqrt(365))

            return {
                "cagr": cagr,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "calmar_ratio": calmar,
                "max_drawdown": max_dd,
                "var_95_daily": var_95,
                "annualized_volatility": volatility
            }

        except Exception as e:
            return {"error": str(e)}
