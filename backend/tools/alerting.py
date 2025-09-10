from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool


class SendInternalAlertInput(BaseModel):
    recipient: str = Field(..., description="The recipient of the alert.")
    message: str = Field(..., description="The alert message.")


class SendInternalAlertOutput(BaseModel):
    success: bool = Field(..., description="Whether the alert was sent successfully.")


@tool(input_schema=SendInternalAlertInput, output_schema=SendInternalAlertOutput)
def SendInternalAlertTool(recipient: str, message: str) -> Dict[str, Any]:
    """
    Sends an internal alert to a specified recipient.
    """
    # ... (Placeholder implementation)
    print(f"ALERT to {recipient}: {message}")
    return {"success": True}
