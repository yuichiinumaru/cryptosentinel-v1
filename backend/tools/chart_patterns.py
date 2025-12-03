from typing import Dict, Any, List

import pandas as pd
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class DetectPatternsInput(BaseModel):
    candles: List[Dict[str, Any]] = Field(..., description="List of candlesticks with open, high, low, close.")


class DetectPatternsOutput(BaseModel):
    patterns: List[str] = Field(..., description="Detected chart patterns.")


def _prepare_dataframe(candles: List[Dict[str, Any]]) -> pd.DataFrame:
    if not candles:
        raise ValueError("At least one candle is required to detect patterns")
    df = pd.DataFrame(candles)
    required_cols = {"open", "high", "low", "close"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing candle fields: {', '.join(missing)}")
    return df.astype(float)


def _detect_bullish_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    current = df.iloc[-1]
    return (prev.close < prev.open) and (current.close > current.open) and (current.close >= prev.open) and (current.open <= prev.close)


def _detect_bearish_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    current = df.iloc[-1]
    return (prev.close > prev.open) and (current.close < current.open) and (current.open >= prev.close) and (current.close <= prev.open)


def _detect_hammer(df: pd.DataFrame) -> bool:
    current = df.iloc[-1]
    body = abs(current.close - current.open)
    lower_shadow = current.open - current.low if current.close >= current.open else current.close - current.low
    upper_shadow = current.high - current.close if current.close >= current.open else current.high - current.open
    return lower_shadow > 2 * body and upper_shadow < body


def _detect_shooting_star(df: pd.DataFrame) -> bool:
    current = df.iloc[-1]
    body = abs(current.close - current.open)
    upper_shadow = current.high - max(current.close, current.open)
    lower_shadow = min(current.close, current.open) - current.low
    return upper_shadow > 2 * body and lower_shadow < body


def detect_chart_patterns(input: DetectPatternsInput) -> DetectPatternsOutput:
    df = _prepare_dataframe(input.candles)
    patterns: List[str] = []
    if _detect_bullish_engulfing(df):
        patterns.append("bullish_engulfing")
    if _detect_bearish_engulfing(df):
        patterns.append("bearish_engulfing")
    if _detect_hammer(df):
        patterns.append("hammer")
    if _detect_shooting_star(df):
        patterns.append("shooting_star")
    return DetectPatternsOutput(patterns=patterns)


chart_patterns_toolkit = Toolkit(name="chart_patterns")
chart_patterns_toolkit.register(detect_chart_patterns)
