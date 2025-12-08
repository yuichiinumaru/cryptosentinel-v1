from typing import Dict, Any, List
import pandas as pd
import numpy as np
import httpx
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

class GetTechIndicatorsInput(BaseModel):
    symbol: str = Field(..., description="The CoinGecko ID of the token (e.g., 'bitcoin').")
    days: int = Field(100, description="Number of days of history to analyze.")

class TechnicalAnalysisToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="technical_analysis", **kwargs)
        self.register(self.get_technical_indicators)

    async def get_technical_indicators(self, input: GetTechIndicatorsInput) -> Dict[str, Any]:
        """
        Calculates technical indicators (RSI, MACD, Bollinger Bands, MA) for a token.
        """
        symbol = input.symbol
        days = input.days

        # 1. Fetch Data
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 429:
                    return {"error": "Rate Limit Exceeded"}
                resp.raise_for_status()
                data = resp.json()

            if "prices" not in data:
                return {"error": "No price data found"}

            df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            prices = df["price"]

            # 2. Calculate Indicators
            results = {}

            # Moving Averages
            results["ma_7"] = float(prices.rolling(window=7).mean().iloc[-1])
            results["ma_25"] = float(prices.rolling(window=25).mean().iloc[-1])
            results["ma_100"] = float(prices.rolling(window=100).mean().iloc[-1])

            # RSI (14)
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            results["rsi_14"] = float(100 - (100 / (1 + rs)).iloc[-1])

            # MACD (12, 26, 9)
            exp1 = prices.ewm(span=12, adjust=False).mean()
            exp2 = prices.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            results["macd"] = float(macd.iloc[-1])
            results["macd_signal"] = float(signal.iloc[-1])
            results["macd_hist"] = float((macd - signal).iloc[-1])

            # Bollinger Bands (20, 2)
            bb_ma = prices.rolling(window=20).mean()
            bb_std = prices.rolling(window=20).std()
            results["bb_upper"] = float((bb_ma + (bb_std * 2)).iloc[-1])
            results["bb_lower"] = float((bb_ma - (bb_std * 2)).iloc[-1])
            results["current_price"] = float(prices.iloc[-1])

            return results

        except Exception as e:
            return {"error": str(e)}
