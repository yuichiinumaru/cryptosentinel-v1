import os

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from web3 import Web3

class GetAccountBalanceInput(BaseModel):
    wallet_address: str = Field(..., description="The wallet address to check.")
    chain: str = Field("ethereum", description="The blockchain to check the balance on.")

class GetAccountBalanceOutput(BaseModel):
    balance: float = Field(..., description="The balance of the wallet.")
    error: str = Field(None, description="An error message if the balance could not be retrieved.")

def get_account_balance(input: GetAccountBalanceInput) -> GetAccountBalanceOutput:
    """
    Gets the balance of a wallet on a given blockchain.
    """
    try:
        rpc_url = os.getenv(f"{input.chain.upper()}_RPC_URL")
        if not rpc_url:
            raise ValueError(f"RPC_URL for chain {input.chain} not found in environment variables.")
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        balance_wei = w3.eth.get_balance(w3.to_checksum_address(input.wallet_address))
        balance = w3.from_wei(balance_wei, 'ether')
        return GetAccountBalanceOutput(balance=float(balance))
    except Exception as e:
        return GetAccountBalanceOutput(balance=0.0, error=str(e))


wallet_toolkit = Toolkit(name="wallet")
wallet_toolkit.register(get_account_balance)
