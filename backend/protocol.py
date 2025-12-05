from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal


class MessageHeader(BaseModel):
    sender: str
    recipient: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message_id: UUID = Field(default_factory=uuid4)
    priority: str = "medium"


class TradeRecommendation(BaseModel):
    header: MessageHeader
    token_address: str
    chain: str
    action: str
    amount: Decimal
    confidence: float # Score 0-1 stays float
    reasoning: str


class TradeApprovalResponse(BaseModel):
    header: MessageHeader
    trade_id: str
    approved: bool
    reason: Optional[str] = None
    tx_hash: Optional[str] = None


class PortfolioUpdate(BaseModel):
    header: MessageHeader
    trade_id: str
    token_address: str
    chain: str
    action: str
    amount: Decimal
    price_per_unit: Decimal
    tx_hash: str


class RiskReportRequest(BaseModel):
    header: MessageHeader
    period: str


class RiskReport(BaseModel):
    header: MessageHeader
    total_value: Decimal
    volatility: float # Statistical metric stays float
    max_drawdown: float # Percentage
    var: float # Value at Risk usually currency, but can be %? Assuming currency -> Decimal.
    # Actually VaR is value. Let's make it Decimal.
    var: Decimal
    risks: List[str]


class StrategyAdjustment(BaseModel):
    header: MessageHeader
    new_instructions: str


class Alert(BaseModel):
    header: MessageHeader
    alert_type: str
    message: str


class TradeOrder(BaseModel):
    """
    A trade order from the DeepTraderManager to a Trader agent.
    """
    header: MessageHeader
    symbol: str = Field(..., description="The symbol of the asset to trade, e.g., 'BTC/USD'")
    action: str = Field(..., description="The action to take, e.g., 'buy', 'sell'")
    quantity: Decimal = Field(..., description="The quantity of the asset to trade")
    order_type: str = Field(..., description="The type of order, e.g., 'market', 'limit'")
    price: Optional[Decimal] = Field(None, description="The limit price for a limit order")


class TradeResult(BaseModel):
    """
    The result of a trade execution, sent from a Trader to the DeepTraderManager.
    """
    header: MessageHeader
    order_id: str = Field(..., description="The unique ID of the order that was executed")
    symbol: str = Field(..., description="The symbol of the asset traded")
    action: str = Field(..., description="The action taken, e.g., 'buy', 'sell'")
    quantity: Decimal = Field(..., description="The quantity of the asset traded")
    price: Decimal = Field(..., description="The average price at which the trade was executed")
    status: str = Field(..., description="The status of the trade, e.g., 'completed', 'failed'")
    timestamp: datetime = Field(default_factory=datetime.now)
