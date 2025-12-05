import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from agno.tools.toolkit import Toolkit
from pycoingecko import CoinGeckoAPI
from pydantic import BaseModel, Field

from backend.storage.models import PortfolioPosition
from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class PortfolioItem(BaseModel):
    token_address: str
    symbol: str
    amount: float
    chain: Optional[str] = None
    coingecko_id: Optional[str] = None
    average_price: Optional[float] = None
    current_price: Optional[float] = None
    value_usd: Optional[float] = None
    last_updated: Optional[datetime] = None


class GetPortfolioOutput(BaseModel):
    items: List[PortfolioItem]
    total_value_usd: float = 0.0
    as_of: datetime = Field(default_factory=datetime.utcnow)


def get_portfolio() -> GetPortfolioOutput:
    storage = _get_storage()
    positions = storage.get_portfolio_positions()
    now = datetime.utcnow()

    coin_ids = {pos.coingecko_id for pos in positions if pos.coingecko_id}
    latest_prices: Dict[str, Dict[str, float]] = {}
    if coin_ids:
        cg = CoinGeckoAPI()
        try:
            latest_prices = cg.get_price(ids=list(coin_ids), vs_currencies="usd")
        except Exception:
            latest_prices = {}

    items: List[PortfolioItem] = []
    for position in positions:
        price: Optional[float] = None
        if position.coingecko_id and position.coingecko_id in latest_prices:
            price = latest_prices[position.coingecko_id].get("usd")
        if price is None:
            price = position.last_price

        value = price * position.amount if price is not None else None
        if value is not None:
            position.last_price = price
            position.last_valuation_usd = value
            position.updated_at = now
            storage.upsert_portfolio_position(position)

        items.append(
            PortfolioItem(
                token_address=position.token_address,
                symbol=position.symbol,
                amount=float(position.amount), # CAST DECIMAL TO FLOAT for response
                chain=position.chain,
                coingecko_id=position.coingecko_id,
                average_price=float(position.average_price),
                current_price=price,
                value_usd=value,
                last_updated=position.updated_at,
            )
        )

    total_value = sum(item.value_usd or 0.0 for item in items)
    return GetPortfolioOutput(items=items, total_value_usd=total_value, as_of=now)


class UpdatePortfolioInput(BaseModel):
    token_address: str
    symbol: str
    amount_change: float = Field(..., description="Positive for buys, negative for sells")
    price: float = Field(..., description="Execution price in USD")
    chain: Optional[str] = Field(None, description="Blockchain network identifier")
    coingecko_id: Optional[str] = Field(None, description="CoinGecko identifier for price retrieval")


def update_portfolio(input: UpdatePortfolioInput) -> None:
    storage = _get_storage()
    positions = {p.token_address: p for p in storage.get_portfolio_positions()}
    token_key = input.token_address.lower()
    now = datetime.utcnow()

    position = positions.get(token_key)
    if position is None and input.amount_change <= 0:
        raise ValueError("Cannot reduce or close a non-existent position")

    if position is None:
        position = PortfolioPosition(
            token_address=token_key,
            symbol=input.symbol,
            chain=input.chain,
            coingecko_id=input.coingecko_id,
            amount=0.0,
            average_price=0.0,
            last_price=None,
            last_valuation_usd=None,
            updated_at=now,
        )

    # Cast to float for calculation if they are Decimal coming from Pydantic,
    # but here they are likely float from input or loaded from DB.
    # To be safe:
    current_amount = float(position.amount)

    new_amount = current_amount + input.amount_change
    if new_amount < -1e-9:
        raise ValueError("Resulting position amount cannot be negative")

    if input.amount_change > 0:
        total_cost = float(position.average_price) * current_amount + input.price * input.amount_change
        position.average_price = total_cost / new_amount if new_amount else input.price
    elif new_amount == 0:
        position.average_price = 0.0

    position.amount = max(new_amount, 0.0)
    position.last_price = input.price
    position.last_valuation_usd = position.amount * input.price if position.amount else 0.0
    position.updated_at = now
    if input.chain:
        position.chain = input.chain
    if input.coingecko_id:
        position.coingecko_id = input.coingecko_id

    storage.upsert_portfolio_position(position)


portfolio_toolkit = Toolkit(name="portfolio")
portfolio_toolkit.register(get_portfolio)
portfolio_toolkit.register(update_portfolio)
