from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class Team(BaseModel):
    name: str
    team_id: Optional[str] = None
    members: List[str]
    description: Optional[str] = None
    instructions: List[str]


class Workflow(BaseModel):
    name: str
    id: Optional[str] = None
    description: Optional[str] = None
    steps: List[str]


class TradeData(BaseModel):
    id: str
    token: str
    action: str
    amount: float
    price: float
    timestamp: datetime
    profit: float
    status: str


class ActivityData(BaseModel):
    id: str
    timestamp: datetime
    type: str
    message: str
    details: Dict[str, Any]


class PortfolioPosition(BaseModel):
    token_address: str
    symbol: str
    chain: Optional[str] = None
    coingecko_id: Optional[str] = None
    amount: float
    average_price: float
    last_price: Optional[float] = None
    last_valuation_usd: Optional[float] = None
    updated_at: datetime


class AlertRecord(BaseModel):
    id: str
    timestamp: datetime
    recipient: str
    channel: str
    message: str
    status: str
    metadata: Dict[str, Any]


class AgentMessageRecord(BaseModel):
    id: str
    timestamp: datetime
    sender: str
    recipient: str
    content: Dict[str, Any]
    status: str
    correlation_id: Optional[str] = None


class KeyValueRecord(BaseModel):
    namespace: str
    key: str
    value: Dict[str, Any]
    updated_at: datetime
