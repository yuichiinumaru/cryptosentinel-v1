from pydantic import BaseModel, Field
from typing import Dict, Any, List
from agno.tools import tool
import pandas as pd
import pandas_ta as ta


class CalculateTechnicalIndicatorInput(BaseModel):
    data: List[Dict[str, float]] = Field(..., description="A list of dictionaries containing the historical data (e.g., ohlcv).")
    indicator: str = Field(..., description="The name of the technical indicator to calculate (e.g., 'rsi', 'macd').")
    params: Dict[str, Any] = Field({}, description="A dictionary of parameters for the indicator.")


class CalculateTechnicalIndicatorOutput(BaseModel):
    result: Any = Field(..., description="The result of the technical indicator calculation.")


@tool(input_schema=CalculateTechnicalIndicatorInput, output_schema=CalculateTechnicalIndicatorOutput)
def CalculateTechnicalIndicator(data: List[Dict[str, float]], indicator: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Calculates a technical indicator from historical data.
    """
    df = pd.DataFrame(data)

    # Ensure the required columns are present
    if not all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']):
        raise ValueError("Data must contain 'open', 'high', 'low', 'close', and 'volume' columns.")

    # Get the indicator function from pandas_ta
    indicator_func = getattr(ta, indicator, None)

    if indicator_func is None:
        raise ValueError(f"Indicator '{indicator}' not found in pandas_ta.")

    # Calculate the indicator
    result = indicator_func(df['close'], **params) # This is a simplification, many indicators need more than just close

    return {"result": result.to_json() if isinstance(result, pd.Series) else result}
