import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage


def _ensure_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    if not data:
        raise ValueError("Historical data is required for strategy evaluation")
    frame = pd.DataFrame(data)
    if "close" not in frame.columns:
        raise ValueError("Historical data must include a 'close' field")
    if "timestamp" in frame.columns:
        frame = frame.sort_values("timestamp")
    frame["close"] = frame["close"].astype(float)
    return frame.reset_index(drop=True)


def _performance_from_returns(returns: pd.Series) -> Tuple[float, float]:
    if returns.empty:
        return 0.0, 0.0
    cumulative = (1 + returns).cumprod()
    total_return = cumulative.iloc[-1] - 1
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    return float(total_return), float(max_drawdown)


class BacktestingInput(BaseModel):
    strategy: str = Field(..., description="The strategy to backtest.")
    data: List[Dict[str, Any]] = Field(..., description="Historical OHLC data.")


class BacktestingOutput(BaseModel):
    results: Dict[str, Any] = Field(..., description="Backtesting metrics.")


def backtesting(input: BacktestingInput) -> BacktestingOutput:
    df = _ensure_dataframe(input.data)
    df["returns"] = df["close"].pct_change().fillna(0)

    strategy = input.strategy.lower()
    if strategy == "sma_cross":
        short_window = 5
        long_window = 21
        df["short_ma"] = df["close"].rolling(short_window).mean()
        df["long_ma"] = df["close"].rolling(long_window).mean()
        df["signal"] = np.where(df["short_ma"] > df["long_ma"], 1, 0)
    elif strategy == "momentum":
        df["signal"] = np.where(df["returns"].rolling(5).mean() > 0, 1, 0)
    else:
        df["signal"] = 1

    df["position"] = df["signal"].shift(1).fillna(0)
    df["strategy_returns"] = df["position"] * df["returns"]

    total_return, max_drawdown = _performance_from_returns(df["strategy_returns"])
    volatility = float(df["strategy_returns"].std() * np.sqrt(252)) if len(df) > 1 else 0.0
    sharpe = (
        float(df["strategy_returns"].mean() / (df["strategy_returns"].std() or 1e-9) * np.sqrt(252))
        if len(df) > 1
        else 0.0
    )
    trade_count = int(df["signal"].diff().fillna(0).abs().sum())

    results = {
        "strategy": input.strategy,
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "annualized_volatility": volatility,
        "sharpe_ratio": sharpe,
        "trade_count": trade_count,
    }
    return BacktestingOutput(results=results)


class StrategyOptimizationInput(BaseModel):
    strategy: str = Field(..., description="The strategy to optimize.")
    data: List[Dict[str, Any]] = Field(..., description="Historical OHLC data.")


class StrategyOptimizationOutput(BaseModel):
    optimized_strategy: str = Field(..., description="Optimized strategy configuration in JSON format.")


def strategy_optimization(input: StrategyOptimizationInput) -> StrategyOptimizationOutput:
    df = _ensure_dataframe(input.data)
    df["returns"] = df["close"].pct_change().fillna(0)
    best_config = {"strategy": input.strategy, "total_return": -np.inf}

    for short_window in range(5, 31, 5):
        for long_window in range(short_window + 5, 61, 5):
            df["short_ma"] = df["close"].rolling(short_window).mean()
            df["long_ma"] = df["close"].rolling(long_window).mean()
            df["signal"] = np.where(df["short_ma"] > df["long_ma"], 1, 0)
            df["position"] = df["signal"].shift(1).fillna(0)
            df["strategy_returns"] = df["position"] * df["returns"]
            total_return, max_drawdown = _performance_from_returns(df["strategy_returns"])
            if total_return > best_config["total_return"]:
                best_config = {
                    "strategy": input.strategy,
                    "short_window": short_window,
                    "long_window": long_window,
                    "total_return": total_return,
                    "max_drawdown": max_drawdown,
                }

    return StrategyOptimizationOutput(optimized_strategy=json.dumps(best_config))


class PaperTradingInput(BaseModel):
    strategy: str = Field(..., description="The strategy to paper trade.")


class PaperTradingOutput(BaseModel):
    results: Dict[str, Any] = Field(..., description="Paper trading state snapshot.")


def paper_trading(input: PaperTradingInput) -> PaperTradingOutput:
    storage = SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))
    state_key = f"paper::{input.strategy.lower()}"
    state = storage.get_state_value("strategy", state_key) or {
        "equity": float(os.getenv("PAPER_TRADING_START_EQUITY", "100000")),
        "simulated_days": 0,
        "updated_at": None,
    }

    daily_return = float(os.getenv("PAPER_TRADING_DAILY_RETURN", "0.001"))
    state["equity"] = float(state["equity"]) * (1 + daily_return)
    state["simulated_days"] = int(state.get("simulated_days", 0)) + 1
    state["updated_at"] = datetime.utcnow().isoformat()

    storage.set_state_value("strategy", state_key, state)
    return PaperTradingOutput(results=state)


strategy_toolkit = Toolkit(name="strategy")
strategy_toolkit.register(backtesting)
strategy_toolkit.register(strategy_optimization)
strategy_toolkit.register(paper_trading)
class StrategyToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="strategy", tools=[
            self.backtesting,
            self.strategy_optimization,
            self.paper_trading,
        ], **kwargs)

    def backtesting(self, input: BacktestingInput) -> BacktestingOutput:
        """
        Backtests a trading strategy.
        """
        # ... (Placeholder implementation)
        return BacktestingOutput(results={"pnl": 1000})

    def strategy_optimization(self, input: StrategyOptimizationInput) -> StrategyOptimizationOutput:
        """
        Optimizes a trading strategy.
        """
        # ... (Placeholder implementation)
        return StrategyOptimizationOutput(optimized_strategy="Optimized strategy")

    def paper_trading(self, input: PaperTradingInput) -> PaperTradingOutput:
        """
        Paper trades a trading strategy.
        """
        # ... (Placeholder implementation)
        return PaperTradingOutput(results={"pnl": 500})

strategy_toolkit = StrategyToolkit()
