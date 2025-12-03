from typing import Dict, Any, List

import pandas as pd
import pandas_ta as ta
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class CalculateTechnicalIndicatorInput(BaseModel):
    data: List[Dict[str, float]] = Field(..., description="OHLCV data points.")
    indicator: str = Field(..., description="Indicator name (sma, rsi, macd).")
    params: Dict[str, Any] = Field(default_factory=dict, description="Indicator-specific parameters.")


class CalculateTechnicalIndicatorOutput(BaseModel):
    result: List[float] = Field(..., description="Indicator series values.")


def calculate_technical_indicator(input: CalculateTechnicalIndicatorInput) -> CalculateTechnicalIndicatorOutput:
    df = pd.DataFrame(input.data)
    if "close" not in df.columns:
        raise ValueError("Data must contain a 'close' column.")

    indicator = input.indicator.lower()
    if indicator == "sma":
        result = ta.sma(df["close"], length=input.params.get("length", 14))
    elif indicator == "rsi":
        result = ta.rsi(df["close"], length=input.params.get("length", 14))
    elif indicator == "macd":
        macd_df = ta.macd(
            df["close"],
            fast=input.params.get("fast", 12),
            slow=input.params.get("slow", 26),
            signal=input.params.get("signal", 9),
        )
        key = f"MACD_{input.params.get('fast', 12)}_{input.params.get('slow', 26)}_{input.params.get('signal', 9)}"
        result = macd_df[key] if macd_df is not None else None
    else:
        raise ValueError(f"Indicator {input.indicator} not supported.")

    if result is None:
        return CalculateTechnicalIndicatorOutput(result=[])
    return CalculateTechnicalIndicatorOutput(result=result.dropna().tolist())


technical_analysis_toolkit = Toolkit(name="technical_analysis")
technical_analysis_toolkit.register(calculate_technical_indicator)
