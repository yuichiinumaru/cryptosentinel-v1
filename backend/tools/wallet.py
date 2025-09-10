import os
from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool
from web3 import Web3


class GetAccountBalanceInput(BaseModel):
    wallet_address: str = Field(..., description="The address of the wallet.")
    chain: str = Field("ethereum", description="The blockchain to check the balance on.")


class GetAccountBalanceOutput(BaseModel):
    balance: str = Field(..., description="The balance of the wallet.")
    error: str = Field(None, description="An error message if the balance could not be retrieved.")


@tool(input_schema=GetAccountBalanceInput, output_schema=GetAccountBalanceOutput)
def GetAccountBalance(wallet_address: str, chain: str = "ethereum") -> Dict[str, Any]:
    """
    Checks the balance of a wallet on a specific blockchain.
    """
    infura_url = os.getenv("INFURA_URL")
    w3 = Web3(Web3.HTTPProvider(infura_url))

    try:
        wallet_address = w3.to_checksum_address(wallet_address)
        balance = w3.eth.get_balance(wallet_address)
        return {"balance": w3.from_wei(balance, "ether")}
    except Exception as e:
        return {"balance": "0", "error": f"Could not get balance: {e}"}


class GetGasPriceInput(BaseModel):
    chain: str = Field("ethereum", description="The blockchain to get the gas price from.")


class GetGasPriceOutput(BaseModel):
    gas_price: str = Field(..., description="The current gas price.")
    error: str = Field(None, description="An error message if the gas price could not be retrieved.")


@tool(input_schema=GetGasPriceInput, output_schema=GetGasPriceOutput)
def GetGasPrice(chain: str = "ethereum") -> Dict[str, Any]:
    """
    Gets the current gas price from a specific blockchain.
    """
    infura_url = os.getenv("INFURA_URL")
    w3 = Web3(Web3.HTTPProvider(infura_url))

    try:
        gas_price = w3.eth.gas_price
        return {"gas_price": w3.from_wei(gas_price, "gwei")}
    except Exception as e:
        return {"gas_price": "0", "error": f"Could not get gas price: {e}"}


class GetTransactionReceiptInput(BaseModel):
    tx_hash: str = Field(..., description="The hash of the transaction.")
    chain: str = Field("ethereum", description="The blockchain the transaction is on.")


class GetTransactionReceiptOutput(BaseModel):
    receipt: Dict[str, Any] = Field(..., description="The transaction receipt.")
    error: str = Field(None, description="An error message if the receipt could not be retrieved.")


@tool(input_schema=GetTransactionReceiptInput, output_schema=GetTransactionReceiptOutput)
def GetTransactionReceipt(tx_hash: str, chain: str = "ethereum") -> Dict[str, Any]:
    """
    Gets the receipt of a transaction.
    """
    infura_url = os.getenv("INFURA_URL")
    w3 = Web3(Web3.HTTPProvider(infura_url))

    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return {"receipt": dict(receipt)}
    except Exception as e:
        return {"receipt": {}, "error": f"Could not get transaction receipt: {e}"}
