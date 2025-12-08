from typing import Dict, Any
import pandas as pd
import numpy as np
import httpx
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from backend.tools.utils import fetch_coingecko_prices

class DetectRegimeInput(BaseModel):
    symbol: str = Field(..., description="The CoinGecko ID of the token.")

class MarketRegimeToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="market_regime", **kwargs)
        self.register(self.detect_market_regime)

    async def detect_market_regime(self, input: DetectRegimeInput) -> Dict[str, Any]:
        """
        Detects the current market regime (Bull/Bear, Volatility state).
        """
        symbol = input.symbol
        days = 365 # Need long history for SMA200

        try:
            async with httpx.AsyncClient() as client:
                try:
                    df = await fetch_coingecko_prices(client, symbol, days)
                except Exception as e:
                    return {"error": f"Failed to fetch data: {e}"}

            prices = df["price"]

            if len(prices) < 200:
                return {"error": "Insufficient data for Regime Detection (Need 200+ days)"}

            # 1. Trend (SMA200 vs Price)
            current_price = prices.iloc[-1]
            sma_50 = prices.rolling(window=50).mean().iloc[-1]
            sma_200 = prices.rolling(window=200).mean().iloc[-1]

            if current_price > sma_200:
                trend = "Bull"
                if sma_50 < sma_200:
                    trend = "Bull (Correction)" # Price above 200, but 50 crossed below? Rare.
            else:
                trend = "Bear"
                if sma_50 > sma_200:
                    trend = "Bear (Recovery)"

            # 2. Volatility (30-day StdDev of returns)
            returns = prices.pct_change().dropna()
            volatility_30d = returns.tail(30).std()

            # Thresholds (Crypto is volatile, let's say 3% daily is High)
            if volatility_30d > 0.04:
                vol_state = "Crisis/High Volatility"
            elif volatility_30d > 0.02:
                vol_state = "Normal Volatility"
            else:
                vol_state = "Low Volatility"

            return {
                "regime": f"{trend} - {vol_state}",
                "trend": trend,
                "volatility_state": vol_state,
                "sma_50": float(sma_50),
                "sma_200": float(sma_200),
                "current_price": float(current_price),
                "volatility_30d": float(volatility_30d)
            }

        except Exception as e:
            return {"error": str(e)}
