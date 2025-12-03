from typing import Dict, Any, List

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.tools.strategy import BacktestingInput, backtesting_func


class MultiStrategyBacktestInput(BaseModel):
    strategies: List[str] = Field(..., description="List of strategy names to backtest.")
    data: List[Dict[str, Any]] = Field(..., description="Historical OHLC data shared across strategies.")


class MultiStrategyBacktestOutput(BaseModel):
    results: Dict[str, Dict[str, Any]] = Field(..., description="Backtest metrics per strategy.")


def run_multi_strategy_backtest(input: MultiStrategyBacktestInput) -> MultiStrategyBacktestOutput:
    """Run multiple strategy backtests over the same dataset and aggregate the results."""
    aggregated: Dict[str, Dict[str, Any]] = {}
    for strategy in input.strategies:
        backtest_result = backtesting_func(BacktestingInput(strategy=strategy, data=input.data))
        aggregated[strategy] = backtest_result.results
    return MultiStrategyBacktestOutput(results=aggregated)


backtesting_toolkit = Toolkit(name="backtesting")
backtesting_toolkit.register(run_multi_strategy_backtest)
