import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.models import AlertRecord
from backend.storage.sqlite import SqliteStorage


class SendInternalAlertInput(BaseModel):
    message: str = Field(..., description="The alert message to send.")
    recipient: str = Field(..., description="Recipient identifier (team or individual).")
    channel: str = Field("internal", description="Logical channel name (ops, risk, trading, etc.).")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the alert payload.")


class SendInternalAlertOutput(BaseModel):
    success: bool = Field(..., description="Whether the alert was sent successfully.")
    alert_id: str = Field(..., description="Identifier of the persisted alert record.")
    delivered_via: List[str] = Field(default_factory=list, description="Delivery mechanisms used (e.g., webhook).")
    error: Optional[str] = Field(None, description="Error details if delivery failed.")


def _build_webhook_payload(alert_id: str, payload: SendInternalAlertInput) -> Dict[str, Any]:
    return {
        "id": alert_id,
        "message": payload.message,
        "recipient": payload.recipient,
        "channel": payload.channel,
        "metadata": payload.metadata,
        "timestamp": datetime.utcnow().isoformat(),
    }


def send_internal_alert(input: SendInternalAlertInput) -> SendInternalAlertOutput:
    storage = SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))
    alert_id = str(uuid.uuid4())
    delivered_via: List[str] = []
    error: Optional[str] = None

    webhook_env_key = f"ALERT_WEBHOOK_URL_{input.channel.upper()}"
    webhook_url = os.getenv(webhook_env_key) or os.getenv("ALERT_WEBHOOK_URL")
    if webhook_url:
        try:
            response = requests.post(webhook_url, json=_build_webhook_payload(alert_id, input), timeout=10)
            response.raise_for_status()
            delivered_via.append("webhook")
        except Exception as exc:  # pragma: no cover - network failure
            error = str(exc)

    alert_record = AlertRecord(
        id=alert_id,
        timestamp=datetime.utcnow(),
        recipient=input.recipient,
        channel=input.channel,
        message=input.message,
        status="delivered" if error is None else "degraded",
        metadata={**input.metadata, "webhook_error": error} if error else input.metadata,
    )
    storage.record_alert(alert_record)

    return SendInternalAlertOutput(success=error is None, alert_id=alert_id, delivered_via=delivered_via, error=error)


alerting_toolkit = Toolkit(name="alerting")
alerting_toolkit.register(send_internal_alert)
