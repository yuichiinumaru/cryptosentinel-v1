import pytest
import pandas as pd
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch
from backend.tools.technical_analysis import TechnicalAnalysisToolkit, GetTechIndicatorsInput
from backend.tools.quant_metrics import QuantitativeAnalysisToolkit, GetQuantMetricsInput
from backend.tools.regime import MarketRegimeToolkit, DetectRegimeInput
from backend.tools.market_correlation import MarketCorrelationToolkit, GetCorrelationInput

# Helper to create mock dataframe
def create_mock_price_df(prices):
    df = pd.DataFrame({'price': prices})
    df.index = pd.date_range(start='2024-01-01', periods=len(prices), freq='D')
    return df

@pytest.mark.asyncio
async def test_technical_analysis():
    # Setup Data: Uptrend
    prices = [100 + i + (i%5) for i in range(100)] # Linear uptrend
    mock_df = create_mock_price_df(prices)

    with patch('backend.tools.technical_analysis.fetch_coingecko_prices', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_df

        toolkit = TechnicalAnalysisToolkit()
        result = await toolkit.get_technical_indicators(GetTechIndicatorsInput(symbol="bitcoin"))

        assert "ma_7" in result
        assert result["current_price"] == prices[-1]
        assert result["ma_25"] < result["current_price"] # Uptrend

@pytest.mark.asyncio
async def test_quant_metrics():
    # Setup Data: Volatile but flat
    prices = [100, 105, 95, 100, 105, 95, 100]
    mock_df = create_mock_price_df(prices)

    with patch('backend.tools.quant_metrics.fetch_coingecko_prices', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_df

        toolkit = QuantitativeAnalysisToolkit()
        result = await toolkit.get_quant_metrics(GetQuantMetricsInput(symbol="bitcoin"))

        assert "sharpe_ratio" in result
        assert "var_95_daily" in result
        assert "max_drawdown" in result

@pytest.mark.asyncio
async def test_market_regime():
    # Setup Data: Bullish
    prices = [100 + i for i in range(200)] # 200 days uptrend
    mock_df = create_mock_price_df(prices)

    with patch('backend.tools.regime.fetch_coingecko_prices', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_df

        toolkit = MarketRegimeToolkit()
        result = await toolkit.detect_market_regime(DetectRegimeInput(symbol="bitcoin"))

        assert result["trend"] == "Bull"
        assert result["sma_50"] > result["sma_200"]

@pytest.mark.asyncio
async def test_market_correlation():
    # Setup Data: Correlated
    prices_a = [100 + i for i in range(50)]
    prices_b = [200 + (i*2) for i in range(50)] # Perfect correlation
    prices_c = [300 + (i*3) for i in range(50)]

    mock_df_a = create_mock_price_df(prices_a)
    mock_df_b = create_mock_price_df(prices_b)
    mock_df_c = create_mock_price_df(prices_c)

    with patch('backend.tools.market_correlation.fetch_coingecko_prices', new_callable=AsyncMock) as mock_fetch:
        # Side effect to return different DFs based on symbol
        mock_fetch.side_effect = [mock_df_a, mock_df_b, mock_df_c]

        toolkit = MarketCorrelationToolkit()
        result = await toolkit.get_market_correlations(GetCorrelationInput(symbol="target"))

        assert result["correlation_btc"] > 0.9 # Should be 1.0 roughly
        assert result["correlation_eth"] > 0.9
