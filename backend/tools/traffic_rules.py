from agno.tools.toolkit import Toolkit
import numpy as np

class TrafficRuleToolkit(Toolkit):
    """
    A toolkit for assessing market congestion using a heuristic model based on RSI and Bollinger Bands.
    """

    def __init__(self):
        super().__init__(name="traffic_rule_toolkit")

    def _calculate_rsi_congestion(self, rsi: float) -> float:
        """Calculates congestion score based on RSI."""
        if rsi > 70:
            return (rsi - 70) / 30  # Scale from 0 to 1 for RSI > 70
        elif rsi < 30:
            return (30 - rsi) / 30  # Scale from 0 to 1 for RSI < 30
        return 0.0

    def _calculate_bb_congestion(self, price: float, upper_band: float, lower_band: float) -> float:
        """Calculates congestion score based on Bollinger Bands."""
        if price > upper_band:
            return min(1.0, (price - upper_band) / (upper_band * 0.05)) # Normalize by 5% above the band
        elif price < lower_band:
            return min(1.0, (lower_band - price) / (lower_band * 0.05)) # Normalize by 5% below the band
        return 0.0

    def get_market_congestion_score(self, rsi: float, price: float, upper_band: float, lower_band: float) -> float:
        """
        Calculates a market congestion score based on RSI and Bollinger Bands.

        The score ranges from 0.0 (no congestion) to 1.0 (high congestion).
        - RSI > 70 or < 30 contributes to the score.
        - Price breaking above the upper or below the lower Bollinger Band contributes to the score.

        Args:
            rsi: The current RSI value.
            price: The current price of the asset.
            upper_band: The upper Bollinger Band value.
            lower_band: The lower Bollinger Band value.

        Returns:
            A congestion score between 0.0 (high congestion) and 1.0 (no congestion).
        """
        rsi_congestion = self._calculate_rsi_congestion(rsi)
        bb_congestion = self._calculate_bb_congestion(price, upper_band, lower_band)

        # Combine the scores, giving more weight to Bollinger Band breakouts
        combined_score = (rsi_congestion * 0.4) + (bb_congestion * 0.6)

        return 1.0 - np.clip(combined_score, 0, 1)
