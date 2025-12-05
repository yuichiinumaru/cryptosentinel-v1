import json
import logging
import os
import asyncio
from decimal import Decimal
from typing import Optional, Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from web3 import Web3, AsyncWeb3
from web3.providers.rpc import AsyncHTTPProvider
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware

# Configure logging
logger = logging.getLogger(__name__)

# Constants
NATIVE_TOKEN_SENTINEL = os.getenv("NATIVE_TOKEN_SENTINEL", "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee").lower()

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}, {"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]')
UNISWAP_ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"}, {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}, {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]')

class Web3Provider:
    """
    Singleton-ish Async Web3 Provider.
    """
    _instances: Dict[str, AsyncWeb3] = {}

    @classmethod
    def get_async_w3(cls, chain: str) -> AsyncWeb3:
        chain = chain.lower()
        if chain not in cls._instances:
            rpc_url = os.getenv(f"{chain.upper()}_RPC_URL")
            if not rpc_url:
                raise ValueError(f"RPC URL for {chain} is not configured.")

            # Use AsyncHTTPProvider
            w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
            cls._instances[chain] = w3
        return cls._instances[chain]

    @staticmethod
    def get_router_address(chain: str, dex: str) -> str:
        DEX_ROUTER_ADDRESSES = {
            "ethereum": {"uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"},
            "bsc": {"pancakeswap_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E"},
            "polygon": {"uniswap_v2": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"},
        }
        try:
            return DEX_ROUTER_ADDRESSES[chain][dex]
        except KeyError:
            raise ValueError(f"Router address not found for {chain}/{dex}")

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


class DexToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="dex_toolkit", **kwargs)
        self.register(self.execute_swap)

    async def execute_swap(self, input: ExecuteSwapInput) -> ExecuteSwapOutput:
        """
        Executes a swap asynchronously. Non-blocking.
        """
        try:
            w3 = Web3Provider.get_async_w3(input.chain)

            if not await w3.is_connected():
                 raise ConnectionError("Async Web3 Node is not connected.")

            account = w3.eth.account.from_key(os.getenv("WALLET_PRIVATE_KEY"))
            router_address = Web3Provider.get_router_address(input.chain, input.dex)

            token_in_addr = w3.to_checksum_address(input.token_in)
            token_out_addr = w3.to_checksum_address(input.token_out)
            router_checksum = w3.to_checksum_address(router_address)

            if input.token_in.lower() == NATIVE_TOKEN_SENTINEL:
                decimals = 18
            else:
                token_contract = w3.eth.contract(address=token_in_addr, abi=ERC20_ABI)
                # FIX: functions.decimals() returns a wrapper, .call() returns coroutine
                # The issue in test was mocking this chain.
                decimals_coro = token_contract.functions.decimals().call()
                # Ensure we await it if it's awaitable (it should be)
                decimals = await decimals_coro

            amount_in_wei = int(input.amount_in * (Decimal(10) ** decimals))

            nonce = await w3.eth.get_transaction_count(account.address)

            if input.token_in.lower() != NATIVE_TOKEN_SENTINEL:
                 allowance = await token_contract.functions.allowance(account.address, router_checksum).call()
                 if allowance < amount_in_wei:
                      logger.info(f"Approving {input.token_in}...")
                      # Gas Price logic
                      # In web3py v7 async, w3.eth.gas_price is awaitable
                      gas_price = await w3.eth.gas_price

                      approve_tx = await token_contract.functions.approve(router_checksum, amount_in_wei).build_transaction({
                          'from': account.address,
                          'nonce': nonce,
                          'gasPrice': gas_price
                      })
                      signed_approve = w3.eth.account.sign_transaction(approve_tx, account.key)
                      tx_hash_approve = await w3.eth.send_raw_transaction(signed_approve.rawTransaction)

                      logger.info(f"Awaiting approval {tx_hash_approve.hex()}...")
                      receipt = await w3.eth.wait_for_transaction_receipt(tx_hash_approve)
                      if receipt['status'] != 1:
                           raise RuntimeError("Approval failed")

                      nonce = await w3.eth.get_transaction_count(account.address)

            router = w3.eth.contract(address=router_checksum, abi=UNISWAP_ROUTER_ABI)
            path = [token_in_addr, token_out_addr]

            amounts_out = await router.functions.getAmountsOut(amount_in_wei, path).call()
            min_out = int(amounts_out[-1] * (1 - input.slippage))

            gas_price = await w3.eth.gas_price

            swap_tx_func = router.functions.swapExactTokensForTokens(
                 amount_in_wei,
                 min_out,
                 path,
                 account.address,
                 int(asyncio.get_event_loop().time()) + 300
            )

            swap_tx = await swap_tx_func.build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gasPrice': gas_price
            })

            signed_swap = w3.eth.account.sign_transaction(swap_tx, account.key)
            tx_hash = await w3.eth.send_raw_transaction(signed_swap.rawTransaction)

            return ExecuteSwapOutput(tx_hash=tx_hash.hex(), success=True)

        except Exception as e:
            logger.exception("Swap failed")
            return ExecuteSwapOutput(tx_hash="", success=False, error=str(e))
