import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.models import AgentMessageRecord
from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


def _dispatch_payload(endpoint_env: str, payload: Dict[str, Any], delivered_via: List[str]) -> None:
    webhook_url = os.getenv(endpoint_env) or os.getenv("COMMUNICATION_WEBHOOK_URL")
    if not webhook_url:
        return
    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
    delivered_via.append("webhook")


def _record_message(
    recipient: str,
    sender: str,
    status: str,
    content: Dict[str, Any],
    correlation_id: str,
) -> AgentMessageRecord:
    storage = _get_storage()
    record = AgentMessageRecord(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        sender=sender,
        recipient=recipient,
        content=content,
        status=status,
        correlation_id=correlation_id,
    )
    storage.record_agent_message(record)
    return record


class ApproveTradeInput(BaseModel):
    trade_id: str = Field(..., description="The ID of the trade to approve.")
    sender: str = Field("DeepTraderManager", description="Agent initiating the approval.")
    recipient: str = Field("Trader", description="Agent receiving the approval.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the approval.")


class ApproveTradeOutput(BaseModel):
    success: bool = Field(..., description="Whether the trade was approved successfully.")
    message_id: str = Field(..., description="Identifier of the stored agent message.")
    delivered_via: List[str] = Field(default_factory=list, description="Delivery mechanisms used.")
    error: str | None = Field(None, description="Error details if the notification failed.")


def approve_trade(input: ApproveTradeInput) -> ApproveTradeOutput:
    content = {
        "type": "trade_approval",
        "trade_id": input.trade_id,
        "metadata": input.metadata,
        "decision": "approved",
    }
    record = _record_message(
        recipient=input.recipient,
        sender=input.sender,
        status="approved",
        content=content,
        correlation_id=input.trade_id,
    )

    delivered_via: List[str] = []
    error: str | None = None
    try:
        payload = {
            "message_id": record.id,
            "event": "trade_approved",
            "trade_id": input.trade_id,
            "metadata": input.metadata,
            "timestamp": datetime.utcnow().isoformat(),
        }
        _dispatch_payload("TRADE_APPROVAL_WEBHOOK_URL", payload, delivered_via)
    except Exception as exc:  # pragma: no cover - external service failure
        error = str(exc)
        storage = _get_storage()
        record.status = "degraded"
        content["delivery_error"] = error
        record.content = content
        storage.record_agent_message(record)

    return ApproveTradeOutput(success=error is None, message_id=record.id, delivered_via=delivered_via, error=error)


class RejectTradeInput(BaseModel):
    trade_id: str = Field(..., description="The ID of the trade to reject.")
    reason: str = Field(..., description="Reason for rejection.")
    sender: str = Field("DeepTraderManager", description="Agent initiating the rejection.")
    recipient: str = Field("Trader", description="Agent receiving the rejection.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the rejection.")


class RejectTradeOutput(BaseModel):
    success: bool = Field(..., description="Whether the trade was rejected successfully.")
    message_id: str = Field(..., description="Identifier of the stored agent message.")
    delivered_via: List[str] = Field(default_factory=list, description="Delivery mechanisms used.")
    error: str | None = Field(None, description="Error details if the notification failed.")


def reject_trade(input: RejectTradeInput) -> RejectTradeOutput:
    content = {
        "type": "trade_rejection",
        "trade_id": input.trade_id,
        "reason": input.reason,
        "metadata": input.metadata,
        "decision": "rejected",
    }
    record = _record_message(
        recipient=input.recipient,
        sender=input.sender,
        status="rejected",
        content=content,
        correlation_id=input.trade_id,
    )

    delivered_via: List[str] = []
    error: str | None = None
    try:
        payload = {
            "message_id": record.id,
            "event": "trade_rejected",
            "trade_id": input.trade_id,
            "reason": input.reason,
            "metadata": input.metadata,
            "timestamp": datetime.utcnow().isoformat(),
        }
        _dispatch_payload("TRADE_REJECTION_WEBHOOK_URL", payload, delivered_via)
    except Exception as exc:  # pragma: no cover - external service failure
        error = str(exc)
        storage = _get_storage()
        record.status = "degraded"
        content["delivery_error"] = error
        record.content = content
        storage.record_agent_message(record)

    return RejectTradeOutput(success=error is None, message_id=record.id, delivered_via=delivered_via, error=error)

class CommunicationToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="communication", tools=[
            self.approve_trade,
            self.reject_trade,
        ], **kwargs)

    def approve_trade(self, input: ApproveTradeInput) -> ApproveTradeOutput:
        """
        Approves a trade.
        """
        # This is a placeholder implementation. A real implementation would send a message to the Trader agent.
        print(f"Trade {input.trade_id} approved.")
        return ApproveTradeOutput(success=True)

    def reject_trade(self, input: RejectTradeInput) -> RejectTradeOutput:
        """
        Rejects a trade.
        """
        # This is a placeholder implementation. A real implementation would send a message to the MarketAnalyst agent.
        print(f"Trade {input.trade_id} rejected. Reason: {input.reason}")
        return RejectTradeOutput(success=True)

communication_toolkit = CommunicationToolkit()

communication_toolkit = Toolkit(name="communication")
communication_toolkit.register(approve_trade)
communication_toolkit.register(reject_trade)
