import os
from typing import Dict, Any

import ccxt
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class ExecuteOrderInput(BaseModel):
    exchange: str = Field(..., description="CEX identifier, e.g., 'binance'.")
    symbol: str = Field(..., description="Trading symbol, e.g., 'BTC/USDT'.")
    type: str = Field(..., description="Order type: 'market' or 'limit'.")
    side: str = Field(..., description="Order side: 'buy' or 'sell'.")
    amount: float = Field(..., description="Quantity to trade.")
    price: float | None = Field(None, description="Limit price (required for limit orders).")


class ExecuteOrderOutput(BaseModel):
    order: Dict[str, Any] = Field(..., description="Exchange order payload.")
    error: str | None = Field(None, description="Error message if execution failed.")


def _build_exchange(exchange_name: str):
    exchange_class = getattr(ccxt, exchange_name)
    client = exchange_class({
        "apiKey": os.getenv(f"{exchange_name.upper()}_API_KEY"),
        "secret": os.getenv(f"{exchange_name.upper()}_API_SECRET"),
    })
    return client


def execute_order(input: ExecuteOrderInput) -> ExecuteOrderOutput:
    try:
        client = _build_exchange(input.exchange)
        if input.type == "limit":
            if input.price is None:
                raise ValueError("Price is required for limit orders")
            order = client.create_limit_order(input.symbol, input.side, input.amount, input.price)
        else:
            order = client.create_market_order(input.symbol, input.side, input.amount)
        return ExecuteOrderOutput(order=order, error=None)
    except Exception as exc:
        return ExecuteOrderOutput(order={}, error=str(exc))


class GetOrderBookInput(BaseModel):
    exchange: str = Field(..., description="CEX identifier, e.g., 'binance'.")
    symbol: str = Field(..., description="Trading symbol to fetch order book for.")


class GetOrderBookOutput(BaseModel):
    order_book: Dict[str, Any] = Field(..., description="Order book snapshot.")
    error: str | None = Field(None, description="Error message if retrieval failed.")


def get_order_book(input: GetOrderBookInput) -> GetOrderBookOutput:
    try:
        client = _build_exchange(input.exchange)
        order_book = client.fetch_order_book(input.symbol)
        return GetOrderBookOutput(order_book=order_book, error=None)
    except Exception as exc:
        return GetOrderBookOutput(order_book={}, error=str(exc))


cex_toolkit = Toolkit(name="cex")
cex_toolkit.register(execute_order)
cex_toolkit.register(get_order_book)
