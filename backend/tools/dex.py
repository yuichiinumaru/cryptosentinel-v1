import json
import logging
import os
import time
from decimal import Decimal
from typing import Optional

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Configure logging
logger = logging.getLogger(__name__)

# Constants
# In a real app, load these from a comprehensive config file or DB
NATIVE_TOKEN_SYMBOLS = {
    "ethereum": "ETH",
    "bsc": "BNB",
    "polygon": "MATIC",
    "avalanche": "AVAX",
    "fantom": "FTM",
    "arbitrum": "ETH",
    "optimism": "ETH",
}
NATIVE_TOKEN_SENTINEL = os.getenv("NATIVE_TOKEN_SENTINEL", "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee").lower()

DEX_ROUTER_ADDRESSES = {
    "ethereum": {"uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"},
    "bsc": {"pancakeswap_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E"},
    "polygon": {"uniswap_v2": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"},
}

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}, {"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]')
UNISWAP_ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"}, {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]')

class WalletManager:
    """
    Manages blockchain connection and account signing.
    """
    def __init__(self, chain: str):
        self.chain = chain.lower()
        self.rpc_var = f"{chain.upper()}_RPC_URL"
        self.rpc_url = os.getenv(self.rpc_var)
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")

        if not self.rpc_url:
            raise ValueError(f"CRITICAL: Environment variable {self.rpc_var} is missing.")
        if not self.private_key:
            raise ValueError("CRITICAL: Environment variable WALLET_PRIVATE_KEY is missing.")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC at {self.rpc_url}")

        if self.chain in ["bsc", "polygon", "avalanche", "fantom"]:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.account = self.w3.eth.account.from_key(self.private_key)

    def get_web3(self):
        return self.w3

    def get_account(self):
        return self.account

    def get_router_address(self, dex: str) -> str:
        chain_routers = DEX_ROUTER_ADDRESSES.get(self.chain)
        if not chain_routers:
            raise ValueError(f"No routers configured for chain: {self.chain}")

        router = chain_routers.get(dex)
        if not router:
            raise ValueError(f"Router {dex} not found for chain {self.chain}")

        return self.w3.to_checksum_address(router)


class ExecuteSwapInput(BaseModel):
    token_in: str = Field(..., description="Address of token to sell")
    token_out: str = Field(..., description="Address of token to buy")
    amount_in: Decimal = Field(..., description="Amount of token_in to sell")
    slippage: float = Field(0.01, description="Slippage tolerance (0.01 = 1%)")
    chain: str = Field("ethereum", description="Blockchain network")
    dex: str = Field("uniswap_v2", description="DEX Protocol")


class ExecuteSwapOutput(BaseModel):
    tx_hash: str
    success: bool
    error: Optional[str] = None


class SimulationInput(BaseModel):
    token_in: str
    token_out: str
    amount_in: Decimal
    chain: str = "ethereum"
    dex: str = "uniswap_v2"


class SimulationOutput(BaseModel):
    simulated_amount_out: Decimal
    gas_estimate: int
    success: bool
    error: Optional[str] = None


class DexToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="dex_toolkit", **kwargs)
        self.register(self.execute_swap)
        self.register(self.simulate_swap)

    def execute_swap(self, input: ExecuteSwapInput) -> ExecuteSwapOutput:
        """
        Executes a swap on the specified DEX.
        """
        try:
            wm = WalletManager(input.chain)
            w3 = wm.get_web3()
            account = wm.get_account()
            router_address = wm.get_router_address(input.dex)

            router = w3.eth.contract(address=router_address, abi=UNISWAP_ROUTER_ABI)
            token_in_addr = w3.to_checksum_address(input.token_in)
            token_out_addr = w3.to_checksum_address(input.token_out)

            # Handle Native Token Logic (Simplified for this exercise, focusing on ERC20 for now as per previous code)
            # Assuming ERC20 to ERC20 for safety based on ABI usage

            token_contract = w3.eth.contract(address=token_in_addr, abi=ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_in_wei = int(input.amount_in * (Decimal(10) ** decimals))

            # 1. Check Allowance
            allowance = token_contract.functions.allowance(account.address, router_address).call()
            if allowance < amount_in_wei:
                logger.info(f"Approving {input.token_in} for {router_address}")
                # SECURITY FIX: Approve EXACT amount, not infinite
                approve_tx = token_contract.functions.approve(router_address, amount_in_wei).build_transaction({
                    'from': account.address,
                    'nonce': w3.eth.get_transaction_count(account.address),
                    'gasPrice': w3.eth.gas_price
                })
                signed_approve = w3.eth.account.sign_transaction(approve_tx, wm.private_key)
                tx_hash_approve = w3.eth.send_raw_transaction(signed_approve.rawTransaction)

                # CRITICAL FIX: Wait for receipt
                logger.info(f"Waiting for approval tx {w3.to_hex(tx_hash_approve)}...")
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash_approve, timeout=300)
                if receipt.status != 1:
                     raise RuntimeError(f"Approval transaction failed: {w3.to_hex(tx_hash_approve)}")
                logger.info("Approval confirmed.")

            # 2. Execute Swap
            path = [token_in_addr, token_out_addr]
            amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()
            expected_out = amounts_out[-1]
            min_out = int(expected_out * (1 - input.slippage))

            deadline = int(time.time()) + 300 # 5 minutes

            # Refresh nonce after approval
            nonce = w3.eth.get_transaction_count(account.address)

            swap_tx = router.functions.swapExactTokensForTokens(
                amount_in_wei,
                min_out,
                path,
                account.address,
                deadline
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gasPrice': w3.eth.gas_price
            })

            signed_swap = w3.eth.account.sign_transaction(swap_tx, wm.private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_swap.rawTransaction)

            # We return the hash immediately, assuming the agent will monitor it,
            # OR we could wait. For high-frequency, async monitoring is better.
            # Given the synchronous tool nature, we return the hash.

            return ExecuteSwapOutput(tx_hash=w3.to_hex(tx_hash), success=True)

        except Exception as e:
            logger.exception("Swap execution failed")
            return ExecuteSwapOutput(tx_hash="", success=False, error=str(e))

    def simulate_swap(self, input: SimulationInput) -> SimulationOutput:
        """
        Simulates a swap to estimate returns.
        """
        try:
            wm = WalletManager(input.chain)
            w3 = wm.get_web3()
            router_address = wm.get_router_address(input.dex)
            router = w3.eth.contract(address=router_address, abi=UNISWAP_ROUTER_ABI)

            token_in = w3.to_checksum_address(input.token_in)
            token_out = w3.to_checksum_address(input.token_out)

            token_contract = w3.eth.contract(address=token_in, abi=ERC20_ABI)
            decimals_in = token_contract.functions.decimals().call()
            amount_in_wei = int(input.amount_in * (Decimal(10) ** decimals_in))

            path = [token_in, token_out]
            # This is a read-only call (simulation)
            amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()

            token_out_contract = w3.eth.contract(address=token_out, abi=ERC20_ABI)
            decimals_out = token_out_contract.functions.decimals().call()

            simulated_out = Decimal(amounts_out[-1]) / (Decimal(10) ** decimals_out)

            return SimulationOutput(
                simulated_amount_out=simulated_out,
                gas_estimate=200000, # Improved estimate
                success=True
            )
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return SimulationOutput(
                simulated_amount_out=Decimal(0),
                gas_estimate=0,
                success=False,
                error=str(e)
            )

# Singleton instance
dex_toolkit = DexToolkit()
