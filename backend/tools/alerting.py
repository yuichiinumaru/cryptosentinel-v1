from pydantic import BaseModel, Field
from agno.tools.toolkit import Toolkit
from agno.tools.function import Function

class SendInternalAlertInput(BaseModel):
    message: str = Field(..., description="The alert message to send.")
    recipient: str = Field(..., description="The recipient of the alert (e.g., 'DeepTraderManager').")

class SendInternalAlertOutput(BaseModel):
    success: bool = Field(..., description="Whether the alert was sent successfully.")

def send_internal_alert(input: SendInternalAlertInput) -> SendInternalAlertOutput:
    """
    Sends an internal alert to another agent or a system channel.
    """
    # This is a placeholder implementation. A real implementation would use a messaging system.
    print(f"ALERT to {input.recipient}: {input.message}")
    return SendInternalAlertOutput(success=True)

alerting_toolkit = Toolkit(name="alerting")
alerting_toolkit.register(send_internal_alert)
