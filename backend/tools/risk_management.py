import os
import uuid
from datetime import datetime
from typing import Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage
from backend.storage.models import ActivityData


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))

class AdjustGlobalRiskParametersInput(BaseModel):
    new_parameters: Dict[str, Any] = Field(..., description="The new risk parameters.")

class AdjustGlobalRiskParametersOutput(BaseModel):
    success: bool = Field(..., description="Whether the parameters were adjusted successfully.")
    applied_parameters: Dict[str, Any] = Field(..., description="Parameters persisted to storage.")


def adjust_global_risk_parameters(input: AdjustGlobalRiskParametersInput) -> AdjustGlobalRiskParametersOutput:
    """Persist global risk parameters for downstream components to consume."""
    storage = _get_storage()
    storage.set_state_value("risk", "global_parameters", input.new_parameters)
    activity = ActivityData(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        type="risk_parameters",
        message="Updated global risk parameters",
        details=input.new_parameters,
    )
    storage.add_activity(activity)
    return AdjustGlobalRiskParametersOutput(success=True, applied_parameters=input.new_parameters)


class PauseTradingInput(BaseModel):
    reason: str = Field(..., description="The reason for pausing trading.")

class PauseTradingOutput(BaseModel):
    success: bool = Field(..., description="Whether trading was paused successfully.")
    status: Dict[str, Any] = Field(..., description="Updated trading pause status.")


def pause_trading(input: PauseTradingInput) -> PauseTradingOutput:
    """Toggle trading pause flag and record the action for auditing."""
    storage = _get_storage()
    status_payload = {
        "paused": True,
        "reason": input.reason,
        "timestamp": datetime.utcnow().isoformat(),
    }
    storage.set_state_value("risk", "trading_status", status_payload)
    activity = ActivityData(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        type="risk_control",
        message="Trading paused",
        details=status_payload,
    )
    storage.add_activity(activity)
    return PauseTradingOutput(success=True, status=status_payload)

risk_management_toolkit = Toolkit(name="risk_management")
risk_management_toolkit.register(adjust_global_risk_parameters)
risk_management_toolkit.register(pause_trading)
class RiskManagementToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="risk_management", tools=[
            self.adjust_global_risk_parameters,
            self.pause_trading,
        ], **kwargs)

    def adjust_global_risk_parameters(self, input: AdjustGlobalRiskParametersInput) -> AdjustGlobalRiskParametersOutput:
        """
        Adjusts the global risk parameters of the system.
        """
        # ... (Placeholder implementation)
        print(f"Risk parameters adjusted to: {input.new_parameters}")
        return AdjustGlobalRiskParametersOutput(success=True)

    def pause_trading(self, input: PauseTradingInput) -> PauseTradingOutput:
        """
        Pauses all trading activities.
        """
        # ... (Placeholder implementation)
        print(f"Trading paused. Reason: {input.reason}")
        return PauseTradingOutput(success=True)

risk_management_toolkit = RiskManagementToolkit()
