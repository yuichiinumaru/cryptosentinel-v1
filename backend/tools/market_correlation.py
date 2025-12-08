from typing import Dict, Any
import httpx
import pandas as pd
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from backend.tools.utils import fetch_coingecko_prices

class GetCorrelationInput(BaseModel):
    symbol: str = Field(..., description="The CoinGecko ID of the token.")
    days: int = Field(30, description="Correlation period (default 30 days).")

class MarketCorrelationToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="market_correlation", **kwargs)
        self.register(self.get_market_correlations)

    async def get_market_correlations(self, input: GetCorrelationInput) -> Dict[str, Any]:
        """
        Calculates correlation with Bitcoin and Ethereum to assess market dependency.
        """
        symbol = input.symbol
        days = input.days

        try:
            async with httpx.AsyncClient() as client:
                # Fetch Target
                try:
                    target_df = await fetch_coingecko_prices(client, symbol, days)
                except Exception as e:
                    return {"error": f"Failed to fetch {symbol}: {e}"}

                # Fetch BTC
                try:
                    btc_df = await fetch_coingecko_prices(client, "bitcoin", days)
                except Exception as e:
                    return {"error": f"Failed to fetch BTC: {e}"}

                # Fetch ETH
                try:
                    eth_df = await fetch_coingecko_prices(client, "ethereum", days)
                except Exception as e:
                    return {"error": f"Failed to fetch ETH: {e}"}

            # Resample to daily close and calculate returns
            target_series = target_df["price"].resample('D').last().pct_change().dropna()
            btc_series = btc_df["price"].resample('D').last().pct_change().dropna()
            eth_series = eth_df["price"].resample('D').last().pct_change().dropna()

            # Align indices (use intersection)
            common_idx = target_series.index.intersection(btc_series.index).intersection(eth_series.index)

            if len(common_idx) < 10:
                return {"error": "Insufficient overlapping data points for correlation"}

            # Calculate Correlation
            corr_btc = target_series[common_idx].corr(btc_series[common_idx])
            corr_eth = target_series[common_idx].corr(eth_series[common_idx])

            # Simple Trend Context (Price vs 30d MA)
            btc_price = btc_df["price"].iloc[-1]
            btc_ma = btc_df["price"].mean()
            btc_trend = "Bullish" if btc_price > btc_ma else "Bearish"

            return {
                "correlation_btc": float(corr_btc),
                "correlation_eth": float(corr_eth),
                "btc_trend_30d": btc_trend,
                "interpretation": self._interpret_correlation(corr_btc)
            }

        except Exception as e:
            return {"error": str(e)}

    def _interpret_correlation(self, corr: float) -> str:
        if corr > 0.8: return "Very High (Shadows Market)"
        if corr > 0.5: return "High Correlation"
        if corr > 0.2: return "Moderate Correlation"
        if corr > -0.2: return "Uncorrelated (Idiosyncratic/Alpha)"
        return "Inverse Correlation (Hedge)"
