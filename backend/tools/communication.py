from pydantic import BaseModel, Field
from agno.tools.toolkit import Toolkit

class ApproveTradeInput(BaseModel):
    trade_id: str = Field(..., description="The ID of the trade to approve.")

class ApproveTradeOutput(BaseModel):
    success: bool = Field(..., description="Whether the trade was approved successfully.")

class RejectTradeInput(BaseModel):
    trade_id: str = Field(..., description="The ID of the trade to reject.")
    reason: str = Field(..., description="The reason for rejecting the trade.")

class RejectTradeOutput(BaseModel):
    success: bool = Field(..., description="Whether the trade was rejected successfully.")

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
