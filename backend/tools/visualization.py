import os
from typing import Dict, Any, List

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class EquityCurveInput(BaseModel):
    limit: int = Field(200, description="Number of recent trades to include.")


class EquityCurveOutput(BaseModel):
    points: List[Dict[str, Any]] = Field(..., description="Equity curve data points.")


def get_equity_curve(input: EquityCurveInput) -> EquityCurveOutput:
    storage = _get_storage()
    trades = storage.get_recent_trades(limit=input.limit)
    equity = 0.0
    points: List[Dict[str, Any]] = []
    for trade in reversed(trades):
        equity += getattr(trade, "profit", 0.0)
        points.append({
            "timestamp": trade.timestamp.isoformat() if hasattr(trade, "timestamp") else None,
            "equity": equity,
            "trade_id": trade.id,
        })
    points.sort(key=lambda p: p["timestamp"] or "")
    return EquityCurveOutput(points=points)


visualization_toolkit = Toolkit(name="visualization")
visualization_toolkit.register(get_equity_curve)
