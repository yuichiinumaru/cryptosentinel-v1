from pydantic import BaseModel, Field
from typing import Dict, Any, List
from agno.tools.toolkit import Toolkit
import pandas as pd
import pandas_ta as ta

class CalculateTechnicalIndicatorInput(BaseModel):
    data: List[Dict[str, float]] = Field(..., description="A list of dictionaries containing the OHLCV data.")
    indicator: str = Field(..., description="The technical indicator to calculate (e.g., 'sma', 'rsi', 'macd').")
    params: Dict[str, Any] = Field({}, description="The parameters for the indicator.")

class CalculateTechnicalIndicatorOutput(BaseModel):
    result: List[float] = Field(..., description="The result of the indicator calculation.")

class TechnicalAnalysisToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="technical_analysis", tools=[self.calculate_technical_indicator], **kwargs)

    def calculate_technical_indicator(self, input: CalculateTechnicalIndicatorInput) -> CalculateTechnicalIndicatorOutput:
        """
        Calculates a technical indicator on the given data.
        """
        df = pd.DataFrame(input.data)
        # This is a simplified implementation. A real implementation would need to handle different indicators and parameters.
        if 'close' not in df.columns:
            raise ValueError("Data must contain a 'close' column.")

        if input.indicator == "sma":
            result = df.ta.sma(length=input.params.get("length", 14), close=df['close'], append=False)
        elif input.indicator == "rsi":
            result = df.ta.rsi(length=input.params.get("length", 14), close=df['close'], append=False)
        elif input.indicator == "macd":
            result = df.ta.macd(fast=input.params.get("fast", 12), slow=input.params.get("slow", 26), signal=input.params.get("signal", 9), close=df['close'], append=False)
        else:
            raise ValueError(f"Indicator {input.indicator} not supported.")

        # The result from pandas_ta can be a DataFrame, so we need to handle it correctly
        if isinstance(result, pd.DataFrame):
            # For MACD, it returns a DataFrame with multiple columns. We can return the main line.
            if input.indicator == "macd":
                result = result[f"MACD_{input.params.get('fast', 12)}_{input.params.get('slow', 26)}_{input.params.get('signal', 9)}"]

        if result is None:
            return CalculateTechnicalIndicatorOutput(result=[])

        return CalculateTechnicalIndicatorOutput(result=result.dropna().tolist())

technical_analysis_toolkit = TechnicalAnalysisToolkit()
