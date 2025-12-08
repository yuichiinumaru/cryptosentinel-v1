from typing import Dict, Any, List
import numpy as np
import httpx
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from backend.tools.utils import fetch_coingecko_prices

class FourierTrendInput(BaseModel):
    symbol: str = Field(..., description="The CoinGecko ID of the token.")
    days: int = Field(100, description="Analysis period.")
    components: int = Field(3, description="Number of FFT components to keep (lower = smoother).")

class FourierToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="math_tools", **kwargs)
        self.register(self.get_fourier_trend)

    async def get_fourier_trend(self, input: FourierTrendInput) -> Dict[str, Any]:
        """
        Uses Fourier Transform (FFT) to denoise price data and find the underlying trend.
        """
        symbol = input.symbol
        days = input.days
        n_components = input.components

        try:
            async with httpx.AsyncClient() as client:
                df = await fetch_coingecko_prices(client, symbol, days)

            prices = df["price"].values
            n = len(prices)

            # FFT
            fft_coeffs = np.fft.fft(prices)

            # Filter: Keep only the first `n_components` frequencies (Low Pass Filter)
            # We copy the array and zero out high frequencies
            fft_filtered = np.copy(fft_coeffs)
            fft_filtered[n_components:-n_components] = 0

            # IFFT
            smoothed = np.fft.ifft(fft_filtered).real

            # Trend Analysis
            current_price = prices[-1]
            smoothed_price = smoothed[-1]
            smoothed_prev = smoothed[-2]

            trend_slope = smoothed_price - smoothed_prev
            trend_direction = "Uptrend" if trend_slope > 0 else "Downtrend"

            # Divergence?
            divergence = current_price - smoothed_price

            return {
                "symbol": symbol,
                "trend_direction": trend_direction,
                "smoothed_price": float(smoothed_price),
                "current_price": float(current_price),
                "divergence": float(divergence),
                "slope": float(trend_slope)
            }

        except Exception as e:
            return {"error": str(e)}
