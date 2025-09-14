from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from agno.tools import tool
from backend.storage.sqlite import SqliteStorage

class PortfolioItem(BaseModel):
    token_address: str
    symbol: str
    amount: float
    current_price: Optional[float] = None
    value_usd: Optional[float] = None

class GetPortfolioOutput(BaseModel):
    items: List[PortfolioItem]
    total_value_usd: float = 0.0

@tool
def get_portfolio() -> GetPortfolioOutput:
    """
    Retrieves the current portfolio from the database and calculates its total value.
    """
    storage = SqliteStorage()
    portfolio_items = storage.get_all_portfolio_items()

    # In a real implementation, you would fetch the current prices for each token
    # and calculate the total value. For this example, we'll use placeholder values.
    for item in portfolio_items:
        item.current_price = 1.0 # Placeholder
        item.value_usd = item.amount * item.current_price

    total_value = sum(item.value_usd for item in portfolio_items if item.value_usd is not None)

    return GetPortfolioOutput(items=portfolio_items, total_value_usd=total_value)

class UpdatePortfolioInput(BaseModel):
    token_address: str
    symbol: str
    amount_change: float
    price: float

@tool
def update_portfolio(input: UpdatePortfolioInput) -> None:
    """
    Updates the portfolio in the database after a trade.
    """
    storage = SqliteStorage()
    storage.update_portfolio_item(
        token_address=input.token_address,
        symbol=input.symbol,
        amount_change=input.amount_change,
        price=input.price
    )
