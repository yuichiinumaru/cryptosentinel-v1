from pydantic import BaseModel, Field
from agno.tools.toolkit import Toolkit
from web3 import Web3
import os
import logging

logger = logging.getLogger(__name__)

class GetAccountBalanceInput(BaseModel):
    wallet_address: str = Field(..., description="The wallet address to check.")
    chain: str = Field("ethereum", description="The blockchain to check the balance on.")

class GetAccountBalanceOutput(BaseModel):
    balance: float = Field(..., description="The balance of the wallet.")
    # Removed 'error' field - we will fail loudly now.

class WalletToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="wallet", **kwargs)
        self.register(self.get_account_balance)

    def get_account_balance(self, input: GetAccountBalanceInput) -> GetAccountBalanceOutput:
        """
        Gets the balance of a wallet on a given blockchain.
        """
        rpc_url = os.getenv(f"{input.chain.upper()}_RPC_URL")
        if not rpc_url:
            raise ValueError(f"RPC_URL for chain {input.chain} not found in environment variables.")

        try:
            # Note: For strict optimization, we should use a shared Web3 provider (Singleton),
            # but for this specific fix, we prioritize Error Handling correctness.
            # The DEX tool fix handles the AsyncWeb3 singleton which should eventually cover this too.
            w3 = Web3(Web3.HTTPProvider(rpc_url))

            if not w3.is_connected():
                 raise ConnectionError(f"Failed to connect to {input.chain} RPC node.")

            checksum_address = w3.to_checksum_address(input.wallet_address)
            balance_wei = w3.eth.get_balance(checksum_address)
            balance = w3.from_wei(balance_wei, 'ether')

            return GetAccountBalanceOutput(balance=float(balance))
        except Exception as e:
            logger.error(f"Wallet balance check failed: {e}")
            # FAIL LOUDLY: Do not return 0.0. Raise the exception so the Agent knows it failed.
            raise RuntimeError(f"Failed to fetch balance for {input.wallet_address} on {input.chain}: {str(e)}")

wallet_toolkit = WalletToolkit()
