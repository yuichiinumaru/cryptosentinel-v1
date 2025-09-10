from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4


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
    amount: float
    confidence: float
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
    amount: float
    price_per_unit: float
    tx_hash: str


class RiskReportRequest(BaseModel):
    header: MessageHeader
    period: str


class RiskReport(BaseModel):
    header: MessageHeader
    total_value: float
    volatility: float
    max_drawdown: float
    var: float
    risks: List[str]


class StrategyAdjustment(BaseModel):
    header: MessageHeader
    new_instructions: str


class Alert(BaseModel):
    header: MessageHeader
    alert_type: str
    message: str
