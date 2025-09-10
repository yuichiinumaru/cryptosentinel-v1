import ccxt
from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool


class ExecuteOrderInput(BaseModel):
    exchange: str = Field(..., description="The CEX to execute the order on.")
    symbol: str = Field(..., description="The symbol to trade (e.g., 'BTC/USDT').")
    type: str = Field(..., description="The type of order ('market' or 'limit').")
    side: str = Field(..., description="The side of the order ('buy' or 'sell').")
    amount: float = Field(..., description="The amount to trade.")
    price: float = Field(None, description="The price for a limit order.")


class ExecuteOrderOutput(BaseModel):
    order: Dict[str, Any] = Field(..., description="The order details.")
    error: str = Field(None, description="An error message if the order failed.")


@tool(input_schema=ExecuteOrderInput, output_schema=ExecuteOrderOutput)
def ExecuteOrder(exchange: str, symbol: str, type: str, side: str, amount: float, price: float = None) -> Dict[str, Any]:
    """
    Executes an order on a CEX.
    """
    try:
        exchange_class = getattr(ccxt, exchange)()
        # ... (Add API key and secret from environment variables)
        if type == 'limit':
            order = exchange_class.create_limit_order(symbol, side, amount, price)
        else:
            order = exchange_class.create_market_order(symbol, side, amount)
        return {"order": order}
    except Exception as e:
        return {"order": {}, "error": f"Could not execute order: {e}"}


class GetOrderBookInput(BaseModel):
    exchange: str = Field(..., description="The CEX to get the order book from.")
    symbol: str = Field(..., description="The symbol to get the order book for.")


class GetOrderBookOutput(BaseModel):
    order_book: Dict[str, Any] = Field(..., description="The order book.")
    error: str = Field(None, description="An error message if the order book could not be retrieved.")


@tool(input_schema=GetOrderBookInput, output_schema=GetOrderBookOutput)
def GetOrderBook(exchange: str, symbol: str) -> Dict[str, Any]:
    """
    Gets the order book for a symbol from a CEX.
    """
    try:
        exchange_class = getattr(ccxt, exchange)()
        order_book = exchange_class.fetch_order_book(symbol)
        return {"order_book": order_book}
    except Exception as e:
        return {"order_book": {}, "error": f"Could not get order book: {e}"}
