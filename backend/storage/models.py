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
