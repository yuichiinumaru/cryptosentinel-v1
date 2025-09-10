from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool


class ApproveTradeInput(BaseModel):
    trade_id: str = Field(..., description="The ID of the trade to approve.")
    reason: str = Field("Approved", description="The reason for the approval.")


class ApproveTradeOutput(BaseModel):
    status: str = Field("approved", description="The approval status.")
    trade_id: str = Field(..., description="The ID of the approved trade.")
    reason: str = Field(..., description="The reason for the approval.")


@tool(input_schema=ApproveTradeInput, output_schema=ApproveTradeOutput)
def ApproveTradeTool(trade_id: str, reason: str = "Approved") -> Dict[str, Any]:
    """
    Approves a trade.
    """
    return {"status": "approved", "trade_id": trade_id, "reason": reason}


class RejectTradeInput(BaseModel):
    trade_id: str = Field(..., description="The ID of the trade to reject.")
    reason: str = Field(..., description="The reason for the rejection.")


class RejectTradeOutput(BaseModel):
    status: str = Field("rejected", description="The rejection status.")
    trade_id: str = Field(..., description="The ID of the rejected trade.")
    reason: str = Field(..., description="The reason for the rejection.")


@tool(input_schema=RejectTradeInput, output_schema=RejectTradeOutput)
def RejectTradeTool(trade_id: str, reason: str) -> Dict[str, Any]:
    """
    Rejects a trade.
    """
    return {"status": "rejected", "trade_id": trade_id, "reason": reason}
