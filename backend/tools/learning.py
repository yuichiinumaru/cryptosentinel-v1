import os
import statistics
import uuid
from datetime import datetime
from typing import Dict, Any, List

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.models import ActivityData
from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class GetTradeHistoryInput(BaseModel):
    limit: int = Field(100, description="Maximum number of trades to retrieve.")


class GetTradeHistoryOutput(BaseModel):
    trades: List[Dict[str, Any]] = Field(..., description="Retrieved trades in dictionary form.")


def get_trade_history(input: GetTradeHistoryInput) -> GetTradeHistoryOutput:
    storage = _get_storage()
    trades = storage.get_recent_trades(limit=input.limit)
    return GetTradeHistoryOutput(trades=[trade.dict() for trade in trades])


class AnalyzePerformanceInput(BaseModel):
    trades: List[Dict[str, Any]] = Field(..., description="Trades to analyze.")


class AnalyzePerformanceOutput(BaseModel):
    performance_metrics: Dict[str, Any] = Field(..., description="Calculated performance metrics.")


def analyze_performance(input: AnalyzePerformanceInput) -> AnalyzePerformanceOutput:
    profits = [float(trade.get("profit", 0)) for trade in input.trades]
    notionals = [float(trade.get("price", 0)) * float(trade.get("amount", 0)) for trade in input.trades]
    total_profit = sum(profits)
    total_notional = sum(notionals)
    roi = total_profit / total_notional if total_notional else 0.0
    win_rate = (sum(1 for p in profits if p > 0) / len(profits)) if profits else 0.0
    avg_profit = statistics.mean(profits) if profits else 0.0
    std_dev = statistics.pstdev(profits) if len(profits) > 1 else 0.0

    metrics = {
        "roi": roi,
        "total_profit": total_profit,
        "total_notional": total_notional,
        "win_rate": win_rate,
        "average_profit": avg_profit,
        "profit_volatility": std_dev,
    }
    return AnalyzePerformanceOutput(performance_metrics=metrics)


class AdjustAgentInstructionsInput(BaseModel):
    agent_id: str = Field(..., description="Agent identifier to update.")
    new_instructions: str = Field(..., description="New instructions for the agent.")


class AdjustAgentInstructionsOutput(BaseModel):
    success: bool = Field(..., description="Whether the update succeeded.")
    updated_at: datetime = Field(..., description="Timestamp of the update.")


def adjust_agent_instructions(input: AdjustAgentInstructionsInput) -> AdjustAgentInstructionsOutput:
    storage = _get_storage()
    timestamp = datetime.utcnow()
    storage.set_state_value(
        "agents",
        f"instructions::{input.agent_id}",
        {"instructions": input.new_instructions, "updated_at": timestamp.isoformat()},
    )
    storage.add_activity(
        ActivityData(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            type="agent_instruction_update",
            message=f"Updated instructions for agent {input.agent_id}",
            details={"agent_id": input.agent_id},
        )
    )
    return AdjustAgentInstructionsOutput(success=True, updated_at=timestamp)


class AdjustToolParametersInput(BaseModel):
    tool_name: str = Field(..., description="Tool name to adjust.")
    new_parameters: Dict[str, Any] = Field(..., description="Parameters to persist.")


class AdjustToolParametersOutput(BaseModel):
    success: bool = Field(..., description="Whether the parameters were saved.")
    applied_parameters: Dict[str, Any] = Field(..., description="Stored parameter set.")


def adjust_tool_parameters(input: AdjustToolParametersInput) -> AdjustToolParametersOutput:
    storage = _get_storage()
    storage.set_state_value("tools", input.tool_name, input.new_parameters)
    storage.add_activity(
        ActivityData(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            type="tool_parameter_update",
            message=f"Updated parameters for tool {input.tool_name}",
            details=input.new_parameters,
        )
    )
    return AdjustToolParametersOutput(success=True, applied_parameters=input.new_parameters)


learning_toolkit = Toolkit(name="learning")
learning_toolkit.register(get_trade_history)
learning_toolkit.register(analyze_performance)
learning_toolkit.register(adjust_agent_instructions)
learning_toolkit.register(adjust_tool_parameters)
class LearningToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="learning", tools=[
            self.get_trade_history,
            self.analyze_performance,
            self.adjust_agent_instructions,
            self.adjust_tool_parameters,
        ], **kwargs)

    def get_trade_history(self, input: GetTradeHistoryInput) -> GetTradeHistoryOutput:
        """
        Gets the trade history from the database.
        """
        # ... (Placeholder implementation)
        return GetTradeHistoryOutput(trades=[])

    def analyze_performance(self, input: AnalyzePerformanceInput) -> AnalyzePerformanceOutput:
        """
        Analyzes the performance of a list of trades.
        """
        # ... (Placeholder implementation)
        return AnalyzePerformanceOutput(performance_metrics={"roi": 0.1})

    def adjust_agent_instructions(self, input: AdjustAgentInstructionsInput) -> AdjustAgentInstructionsOutput:
        """
        Adjusts the instructions of an agent.
        """
        # ... (Placeholder implementation)
        return AdjustAgentInstructionsOutput(success=True)

    def adjust_tool_parameters(self, input: AdjustToolParametersInput) -> AdjustToolParametersOutput:
        """
        Adjusts the parameters of a tool.
        """
        # ... (Placeholder implementation)
        return AdjustToolParametersOutput(success=True)

learning_toolkit = LearningToolkit()
