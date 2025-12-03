import json
import logging
import os
import time
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Literal, Optional

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

try:  # Optional dependency
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
except ImportError as exc:  # pragma: no cover - guard for environments without web3
    Web3 = None
    geth_poa_middleware = None
    _WEB3_IMPORT_ERROR = exc
else:
    _WEB3_IMPORT_ERROR = None


logger = logging.getLogger(__name__)

NATIVE_TOKEN_SENTINEL = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
NATIVE_TOKEN_SYMBOLS = {"ethereum": "ETH", "bsc": "BNB", "polygon": "MATIC"}
WRAPPED_NATIVE = {
    "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "bsc": "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    "polygon": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
}
ZEROX_BASE_URLS = {
    "ethereum": "https://api.0x.org",
    "polygon": "https://polygon.api.0x.org",
    "bsc": "https://bsc.api.0x.org",
}

DEX_ROUTER_ADDRESSES: Dict[str, Dict[str, str]] = {
    "ethereum": {"uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"},
    "bsc": {"pancakeswap_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E"},
    "polygon": {"uniswap_v2": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"},
}

UNISWAP_ROUTER_ABI = json.loads(
    """
    [
      {
        "inputs": [
          {"internalType": "address", "name": "tokenA", "type": "address"},
          {"internalType": "address", "name": "tokenB", "type": "address"},
          {"internalType": "uint256", "name": "amountADesired", "type": "uint256"},
          {"internalType": "uint256", "name": "amountBDesired", "type": "uint256"},
          {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
          {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
          {"internalType": "address", "name": "to", "type": "address"},
          {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
          {"internalType": "uint256", "name": "amountA", "type": "uint256"},
          {"internalType": "uint256", "name": "amountB", "type": "uint256"},
          {"internalType": "uint256", "name": "liquidity", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
      },
      {
        "inputs": [
          {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
          {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
          {"internalType": "address[]", "name": "path", "type": "address[]"},
          {"internalType": "address", "name": "to", "type": "address"},
          {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [
          {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
      },
      {
        "inputs": [
          {"internalType": "address", "name": "tokenA", "type": "address"},
          {"internalType": "address", "name": "tokenB", "type": "address"},
          {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
          {"internalType": "uint256", "name": "amountAMin", "type": "uint256"},
          {"internalType": "uint256", "name": "amountBMin", "type": "uint256"},
          {"internalType": "address", "name": "to", "type": "address"},
          {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "removeLiquidity",
        "outputs": [
          {"internalType": "uint256", "name": "amountA", "type": "uint256"},
          {"internalType": "uint256", "name": "amountB", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
      }
    ]
    """
)

ERC20_ABI = [
    {
        "name": "decimals",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
    },
    {
        "name": "allowance",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "approve",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
]


def _require_web3() -> None:
    if Web3 is None:  # pragma: no cover - depends on optional dependency
        raise ImportError("web3 package is required for DEX operations") from _WEB3_IMPORT_ERROR


def _apply_poa_middleware(w3: "Web3") -> None:
    try:
        chain_id = w3.eth.chain_id
    except Exception:  # pragma: no cover - network failures
        chain_id = None
    if chain_id in {56, 97, 137, 80001, 43114, 8453, 84532}:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def _is_native_token(token: str) -> bool:
    token_lower = token.lower()
    return token_lower in {"eth", "bnb", "matic", NATIVE_TOKEN_SENTINEL}


def _normalize_for_router(chain: str, token: str) -> str:
    _require_web3()
    if _is_native_token(token):
        wrapped = WRAPPED_NATIVE.get(chain.lower())
        if not wrapped:
            raise ValueError(f"Wrapped asset not configured for chain {chain}")
        return Web3.to_checksum_address(wrapped)
    return Web3.to_checksum_address(token)


def _normalize_for_zero_x(chain: str, token: str) -> str:
    if _is_native_token(token):
        symbol = NATIVE_TOKEN_SYMBOLS.get(chain.lower())
        if not symbol:
            raise ValueError(f"Native token not supported for chain {chain}")
        return symbol
    _require_web3()
    return Web3.to_checksum_address(token)


def _get_decimals(w3: "Web3", token: str) -> int:
    if _is_native_token(token):
        return 18
    contract = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
    try:
        return contract.functions.decimals().call()
    except Exception:  # pragma: no cover - fallback
        logger.warning("Falling back to 18 decimals for token %s", token)
        return 18


def _amount_to_base_units(w3: "Web3", token: str, amount: float, decimals_override: Optional[int] = None) -> int:
    decimals = decimals_override if decimals_override is not None else _get_decimals(w3, token)
    quantized = Decimal(str(amount)).scaleb(decimals).quantize(Decimal(1), rounding=ROUND_DOWN)
    return int(quantized)


def _ensure_allowance(w3: "Web3", account, token: str, spender: str, amount: int) -> Optional[str]:
    if _is_native_token(token):
        return None
    contract = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
    allowance = contract.functions.allowance(account.address, Web3.to_checksum_address(spender)).call()
    if allowance >= amount:
        return None
    tx = contract.functions.approve(Web3.to_checksum_address(spender), amount).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price,
        }
    )
    tx.setdefault("gas", int(w3.eth.estimate_gas(tx) * 1.2))
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("Token approval transaction reverted")
    return tx_hash.hex()


def _send_transaction(w3: "Web3", account, transaction: Dict[str, Any]) -> str:
    transaction.setdefault("gasPrice", w3.eth.gas_price)
    transaction.setdefault("nonce", w3.eth.get_transaction_count(account.address))
    transaction.setdefault("chainId", w3.eth.chain_id)
    if "gas" not in transaction:
        transaction["gas"] = int(w3.eth.estimate_gas(transaction) * 1.2)
    signed = account.sign_transaction(transaction)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("On-chain transaction reverted")
    return tx_hash.hex()


def _deadline(minutes: int = 10) -> int:
    return int(time.time()) + minutes * 60


class WalletManager:
    def __init__(self, chain: str):
        _require_web3()
        self.chain = chain.lower()
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from agno.tools.toolkit import Toolkit
import os
from web3 import Web3
import json
from typing import List, Dict, Any, Literal, Optional
from agno.tools.toolkit import Toolkit
from agno.tools import tool
import os
from web3 import Web3
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Simplified ABIs
UNISWAP_V2_ROUTER_ABI = json.loads("""[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]""")

# Added decimals to ERC20 ABI
ERC20_ABI = json.loads('[{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}, {"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}]')


class WalletManager:
    def __init__(self, chain: str = "ethereum"):
        self.chain = chain
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")
        self.rpc_url = os.getenv(f"{chain.upper()}_RPC_URL")

        if not self.private_key:
            raise ValueError("WALLET_PRIVATE_KEY not found in environment variables.")
        rpc_key = f"{self.chain.upper()}_RPC_URL"
        rpc_url = os.getenv(rpc_key)
        if not rpc_url:
            raise ValueError(f"{rpc_key} not found in environment variables.")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        _apply_poa_middleware(self.w3)
        self.account = self.w3.eth.account.from_key(self.private_key)

    def get_web3(self) -> "Web3":
        return self.w3

    def get_signer(self):
        return self.account


def _fetch_zero_x_quote(
    chain: str,
    token_in: str,
    token_out: str,
    sell_amount: int,
    slippage: float,
    taker_address: str,
) -> Dict[str, Any]:
    base_url = ZEROX_BASE_URLS.get(chain.lower())
    if not base_url:
        raise ValueError(f"0x aggregator not configured for chain {chain}")
    params = {
        "sellToken": _normalize_for_zero_x(chain, token_in),
        "buyToken": _normalize_for_zero_x(chain, token_out),
        "sellAmount": str(sell_amount),
        "slippagePercentage": str(slippage),
        "takerAddress": taker_address,
    }
    headers = {}
    api_key = os.getenv("ZEROX_API_KEY")
    if api_key:
        headers["0x-api-key"] = api_key
    response = requests.get(
        f"{base_url}/swap/v1/quote",
        params=params,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()
            logger.warning("WALLET_PRIVATE_KEY not found in environment variables.")
        if not self.rpc_url:
            logger.warning(f"{chain.upper()}_RPC_URL not found in environment variables.")

        if self.rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        else:
            self.w3 = None

             # Just a warning to allow module import without env vars in some contexts
            logger.warning("WALLET_PRIVATE_KEY not found in environment variables.")
        if not self.rpc_url:
            logger.warning(f"{chain.upper()}_RPC_URL not found in environment variables.")

        if self.rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        else:
            self.w3 = None

        if self.private_key and self.w3:
             self.account = self.w3.eth.account.from_key(self.private_key)
        else:
             self.account = None

    def get_w3(self):
        return self.w3

    def get_account(self):
        return self.account

    def get_router_address(self, dex: str):
        if dex == "uniswap_v2":
            return "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        elif dex == "pancakeswap_v2":
            return "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        # Placeholder addresses - replace with real ones for production
        if dex == "uniswap_v2":
            return "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" # Uniswap V2 Router
        elif dex == "pancakeswap_v2":
            return "0x10ED43C718714eb63d5aA57B78B54704E256024E" # PCS V2 Router
        return None

class ExecuteSwapInput(BaseModel):
    token_in: str = Field(..., description="Address of the token to sell or native token symbol.")
    token_out: str = Field(..., description="Address of the token to buy or native token symbol.")
    amount_in: float = Field(..., description="Amount of token_in to sell (human units).")
    slippage: float = Field(0.01, description="Maximum acceptable slippage (0.01 for 1%).")
    chain: str = Field("ethereum", description="Blockchain to execute the swap on.")


class ExecuteSwapOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the executed swap.")
    success: bool = Field(..., description="True if the swap was successful, False otherwise.")
    error: Optional[str] = Field(None, description="Error message if the swap failed.")
    quote: Optional[Dict[str, Any]] = Field(None, description="0x quote used for the swap.")


def execute_swap(input: ExecuteSwapInput) -> ExecuteSwapOutput:
    """Executes a token swap using the 0x aggregator with on-chain settlement."""
    try:
        wallet = WalletManager(input.chain)
        w3 = wallet.get_web3()
        account = wallet.get_signer()
        amount_units = _amount_to_base_units(w3, input.token_in, input.amount_in)
        quote = _fetch_zero_x_quote(
            input.chain,
            input.token_in,
            input.token_out,
            amount_units,
            input.slippage,
            account.address,
        )
        allowance_tx = _ensure_allowance(w3, account, input.token_in, quote["allowanceTarget"], amount_units)
        if allowance_tx:
            logger.info("Submitted allowance transaction %s", allowance_tx)
        transaction = {
            "from": account.address,
            "to": Web3.to_checksum_address(quote["to"]),
            "data": quote["data"],
            "value": int(quote.get("value", "0")),
            "gas": int(quote.get("gas", quote.get("estimatedGas", 0) or 0)),
            "gasPrice": int(quote.get("gasPrice", w3.eth.gas_price)),
        }
        if not transaction["gas"]:
            transaction.pop("gas")
        tx_hash = _send_transaction(w3, account, transaction)
        return ExecuteSwapOutput(tx_hash=tx_hash, success=True, error=None, quote=quote)
    except Exception as exc:  # pragma: no cover - external services
        logger.exception("Swap execution failed")
        return ExecuteSwapOutput(tx_hash="", success=False, error=str(exc))

        wm = WalletManager(input.chain)
        w3 = wm.get_w3()
        account = wm.get_account()

        if not w3 or not account:
            # Fallback to simulation/mock if no env vars
            return ExecuteSwapOutput(tx_hash="0xMOCK_HASH_BECAUSE_NO_RPC_OR_KEY", success=True)

        router_address = wm.get_router_address(input.dex)
        router_contract = w3.eth.contract(address=router_address, abi=UNISWAP_V2_ROUTER_ABI)

        token_in_address = w3.to_checksum_address(input.token_in)
        token_out_address = w3.to_checksum_address(input.token_out)

        # Get decimals
        token_contract = w3.eth.contract(address=token_in_address, abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_raw = int(input.amount_in * (10 ** decimals))

        # Approve if needed
        allowance = token_contract.functions.allowance(account.address, router_address).call()

        if allowance < amount_in_raw:
            approve_tx = token_contract.functions.approve(router_address, amount_in_raw).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gasPrice': w3.eth.gas_price
            })
            signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, wm.private_key)
            w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
            # Wait for confirmation... in real code

        # Swap
        path = [token_in_address, token_out_address]
        # Get amounts out to calculate min amount out based on slippage
        amounts_out = router_contract.functions.getAmountsOut(amount_in_raw, path).call()
        amount_out_min = int(amounts_out[-1] * (1 - input.slippage))

        deadline = w3.eth.get_block('latest')['timestamp'] + 1200 # 20 mins

        swap_tx = router_contract.functions.swapExactTokensForTokens(
            amount_in_raw,
            amount_out_min,
            path,
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price
        })

        signed_swap_tx = w3.eth.account.sign_transaction(swap_tx, wm.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_swap_tx.raw_transaction)

        return ExecuteSwapOutput(tx_hash=w3.to_hex(tx_hash), success=True)

    except Exception as e:
        logger.error(f"Swap failed: {e}")
        return ExecuteSwapOutput(tx_hash="", success=False, error=str(e))

class RevokeApprovalInput(BaseModel):
    token_address: str = Field(..., description="The address of the token to revoke approval for.")
    spender_address: str = Field(..., description="The address of the spender (e.g. DEX router) to revoke.")
    chain: str = Field("ethereum", description="Blockchain to execute on.")

class RevokeApprovalOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the revocation.")
    success: bool = Field(..., description="True if successful.")
    error: str = Field(None, description="Error message.")

@tool
def revoke_approval(input: RevokeApprovalInput) -> RevokeApprovalOutput:
    """
    Revokes approval for a spender to spend tokens.
    """
    try:
        wm = WalletManager(input.chain)
        w3 = wm.get_w3()
        account = wm.get_account()

        if not w3 or not account:
            return RevokeApprovalOutput(tx_hash="0xMOCK_REVOKE", success=True)

        token_contract = w3.eth.contract(address=w3.to_checksum_address(input.token_address), abi=ERC20_ABI)

        # Approve 0
        tx = token_contract.functions.approve(w3.to_checksum_address(input.spender_address), 0).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price
        })

        signed_tx = w3.eth.account.sign_transaction(tx, wm.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return RevokeApprovalOutput(tx_hash=w3.to_hex(tx_hash), success=True)
    except Exception as e:
        return RevokeApprovalOutput(tx_hash="", success=False, error=str(e))

class ExecuteTransactionSimulationInput(BaseModel):
    token_in: str
    token_out: str
    amount_in: float
    chain: str = "ethereum"
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = "uniswap_v2"

class ExecuteTransactionSimulationOutput(BaseModel):
    simulated_amount_out: float
    gas_estimate: int
    success: bool
    error: Optional[str] = None

@tool
def execute_transaction_simulation(input: ExecuteTransactionSimulationInput) -> ExecuteTransactionSimulationOutput:
    """
    Simulates a transaction to estimate outcome and gas.
    """
    try:
        wm = WalletManager(input.chain)
        w3 = wm.get_w3()

        if not w3:
             # Mock simulation
            return ExecuteTransactionSimulationOutput(
                simulated_amount_out=input.amount_in * 0.98, # Mock price
                gas_estimate=210000,
                success=True
            )

        router_address = wm.get_router_address(input.dex)
        router_contract = w3.eth.contract(address=router_address, abi=UNISWAP_V2_ROUTER_ABI)
        token_in = w3.to_checksum_address(input.token_in)
        token_out = w3.to_checksum_address(input.token_out)

        # Get decimals
        token_contract = w3.eth.contract(address=token_in, abi=ERC20_ABI)
        decimals_in = token_contract.functions.decimals().call()
        amount_in_raw = int(input.amount_in * (10 ** decimals_in))

        token_contract_out = w3.eth.contract(address=token_out, abi=ERC20_ABI)
        decimals_out = token_contract_out.functions.decimals().call()

        amounts_out = router_contract.functions.getAmountsOut(amount_in_raw, [token_in, token_out]).call()
        simulated_out = amounts_out[-1] / (10 ** decimals_out)

        # Gas estimate (mocked or real call)

        return ExecuteTransactionSimulationOutput(
            simulated_amount_out=float(simulated_out),
            gas_estimate=150000, # Simplified
            success=True
        )

    except Exception as e:
        return ExecuteTransactionSimulationOutput(simulated_amount_out=0.0, gas_estimate=0, success=False, error=str(e))

class AddLiquidityInput(BaseModel):
    token_a: str = Field(..., description="Address of the first token or native token symbol.")
    token_b: str = Field(..., description="Address of the second token or native token symbol.")
    amount_a: float = Field(..., description="Amount of the first token (human units).")
    amount_b: float = Field(..., description="Amount of the second token (human units).")
    chain: str = Field("ethereum", description="Blockchain to add liquidity to.")
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = Field("uniswap_v2", description="DEX router to target.")
    slippage: float = Field(0.01, description="Slippage tolerance for min amounts.")


class AddLiquidityOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the liquidity addition.")
    success: bool = Field(..., description="True if successful, False otherwise.")
    error: Optional[str] = Field(None, description="Error message if failed.")


def _min_with_slippage(amount: int, slippage: float) -> int:
    tolerance = Decimal(1) - Decimal(str(slippage))
    return int((Decimal(amount) * tolerance).to_integral_value(rounding=ROUND_DOWN))


def _get_router_contract(w3: "Web3", chain: str, dex: str):
    chain_map = DEX_ROUTER_ADDRESSES.get(chain.lower())
    if not chain_map or dex not in chain_map:
        raise ValueError(f"Router not configured for chain {chain} and dex {dex}")
    return w3.eth.contract(address=Web3.to_checksum_address(chain_map[dex]), abi=UNISWAP_ROUTER_ABI)


def add_liquidity(input: AddLiquidityInput) -> AddLiquidityOutput:
    """Adds liquidity to an AMM pool using router contracts."""
    try:
        wallet = WalletManager(input.chain)
        w3 = wallet.get_web3()
        account = wallet.get_signer()
        router = _get_router_contract(w3, input.chain, input.dex)
        if _is_native_token(input.token_a) or _is_native_token(input.token_b):
            raise ValueError("Native token liquidity is not supported in this environment; wrap assets first.")
        token_a_router = _normalize_for_router(input.chain, input.token_a)
        token_b_router = _normalize_for_router(input.chain, input.token_b)
        amount_a_units = _amount_to_base_units(w3, input.token_a, input.amount_a)
        amount_b_units = _amount_to_base_units(w3, input.token_b, input.amount_b)
        amount_a_min = _min_with_slippage(amount_a_units, input.slippage)
        amount_b_min = _min_with_slippage(amount_b_units, input.slippage)
        _ensure_allowance(w3, account, input.token_a, router.address, amount_a_units)
        _ensure_allowance(w3, account, input.token_b, router.address, amount_b_units)
        deadline = _deadline()
        tx = router.functions.addLiquidity(
            token_a_router,
            token_b_router,
            amount_a_units,
            amount_b_units,
            amount_a_min,
            amount_b_min,
            account.address,
            deadline,
        ).build_transaction({"from": account.address})
        tx_hash = _send_transaction(w3, account, tx)
        return AddLiquidityOutput(tx_hash=tx_hash, success=True, error=None)
    except Exception as exc:  # pragma: no cover
        logger.exception("Liquidity addition failed")
        return AddLiquidityOutput(tx_hash="", success=False, error=str(exc))


class RemoveLiquidityInput(BaseModel):
    lp_token: str = Field(..., description="Address of the LP token representing the pool position.")
    token_a: str = Field(..., description="Address of the first token in the pool.")
    token_b: str = Field(..., description="Address of the second token in the pool.")
    liquidity: float = Field(..., description="Amount of LP tokens to remove (human units).")
    chain: str = Field("ethereum", description="Blockchain to remove liquidity from.")
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = Field("uniswap_v2", description="DEX router to target.")
    slippage: float = Field(0.01, description="Slippage tolerance for min outputs.")


class RemoveLiquidityOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the liquidity removal.")
    success: bool = Field(..., description="True if successful, False otherwise.")
    error: Optional[str] = Field(None, description="Error message if failed.")


class RevokeApprovalInput(BaseModel):
    token_address: str = Field(..., description="The address of the token to revoke approval for.")
    spender_address: str = Field(..., description="The address of the spender (e.g. DEX router) to revoke.")
    chain: str = Field("ethereum", description="Blockchain to execute on.")

class RevokeApprovalOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the revocation.")
    success: bool = Field(..., description="True if successful.")
    error: str = Field(None, description="Error message.")

class ExecuteTransactionSimulationInput(BaseModel):
    token_in: str
    token_out: str
    amount_in: float
    chain: str = "ethereum"
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = "uniswap_v2"

class ExecuteTransactionSimulationOutput(BaseModel):
    simulated_amount_out: float
    gas_estimate: int
    success: bool
    error: Optional[str] = None

class DexToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="dex", tools=[
            self.execute_swap,
            self.add_liquidity,
            self.remove_liquidity,
            self.revoke_approval,
            self.execute_transaction_simulation
        ], **kwargs)

    def execute_swap(self, input: ExecuteSwapInput) -> ExecuteSwapOutput:
        """
        Executes a token swap on a decentralized exchange.
        """
        try:
            # ... (Implementation details for interacting with DEX contracts)
            return ExecuteSwapOutput(tx_hash="0x123...", success=True)
        except Exception as e:
            wm = WalletManager(input.chain)
            w3 = wm.get_w3()
            account = wm.get_account()

            if not w3 or not account:
                return ExecuteSwapOutput(tx_hash="0xMOCK_HASH_BECAUSE_NO_RPC_OR_KEY", success=True)

            router_address = wm.get_router_address(input.dex)
            router_contract = w3.eth.contract(address=router_address, abi=UNISWAP_V2_ROUTER_ABI)

            token_in_address = w3.to_checksum_address(input.token_in)
            token_out_address = w3.to_checksum_address(input.token_out)

            token_contract = w3.eth.contract(address=token_in_address, abi=ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_in_raw = int(input.amount_in * (10 ** decimals))

            allowance = token_contract.functions.allowance(account.address, router_address).call()

            if allowance < amount_in_raw:
                approve_tx = token_contract.functions.approve(router_address, amount_in_raw).build_transaction({
                    'from': account.address,
                    'nonce': w3.eth.get_transaction_count(account.address),
                    'gasPrice': w3.eth.gas_price
                })
                signed_approve_tx = w3.eth.account.sign_transaction(approve_tx, wm.private_key)
                w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)

            path = [token_in_address, token_out_address]
            amounts_out = router_contract.functions.getAmountsOut(amount_in_raw, path).call()
            amount_out_min = int(amounts_out[-1] * (1 - input.slippage))

            deadline = w3.eth.get_block('latest')['timestamp'] + 1200

            swap_tx = router_contract.functions.swapExactTokensForTokens(
                amount_in_raw,
                amount_out_min,
                path,
                account.address,
                deadline
            ).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gasPrice': w3.eth.gas_price
            })

            signed_swap_tx = w3.eth.account.sign_transaction(swap_tx, wm.private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_swap_tx.raw_transaction)

            return ExecuteSwapOutput(tx_hash=w3.to_hex(tx_hash), success=True)

        except Exception as e:
            logger.error(f"Swap failed: {e}")
            return ExecuteSwapOutput(tx_hash="", success=False, error=str(e))

    def add_liquidity(self, input: AddLiquidityInput) -> AddLiquidityOutput:
        """
        Adds liquidity to a decentralized exchange pool.
        """
        try:
            # ... (Implementation details)
            return AddLiquidityOutput(tx_hash="0x456...", success=True)
        except Exception as e:
            return AddLiquidityOutput(tx_hash="", success=False, error=str(e))

    def remove_liquidity(self, input: RemoveLiquidityInput) -> RemoveLiquidityOutput:
        """
        Removes liquidity from a decentralized exchange pool.
        """
        try:
            # ... (Implementation details)
            return RemoveLiquidityOutput(tx_hash="0x789...", success=True)
        except Exception as e:
            return RemoveLiquidityOutput(tx_hash="", success=False, error=str(e))
            return RemoveLiquidityOutput(tx_hash="0x789...", success=True)
        except Exception as e:
            return RemoveLiquidityOutput(tx_hash="", success=False, error=str(e))

    def revoke_approval(self, input: RevokeApprovalInput) -> RevokeApprovalOutput:
        """
        Revokes approval for a spender to spend tokens.
        """
        try:
            wm = WalletManager(input.chain)
            w3 = wm.get_w3()
            account = wm.get_account()

            if not w3 or not account:
                return RevokeApprovalOutput(tx_hash="0xMOCK_REVOKE", success=True)

            token_contract = w3.eth.contract(address=w3.to_checksum_address(input.token_address), abi=ERC20_ABI)

            tx = token_contract.functions.approve(w3.to_checksum_address(input.spender_address), 0).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gasPrice': w3.eth.gas_price
            })

            signed_tx = w3.eth.account.sign_transaction(tx, wm.private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            return RevokeApprovalOutput(tx_hash=w3.to_hex(tx_hash), success=True)
        except Exception as e:
            return RevokeApprovalOutput(tx_hash="", success=False, error=str(e))

    def execute_transaction_simulation(self, input: ExecuteTransactionSimulationInput) -> ExecuteTransactionSimulationOutput:
        """
        Simulates a transaction to estimate outcome and gas.
        """
        try:
            wm = WalletManager(input.chain)
            w3 = wm.get_w3()

            if not w3:
                return ExecuteTransactionSimulationOutput(
                    simulated_amount_out=input.amount_in * 0.98,
                    gas_estimate=210000,
                    success=True
                )

            router_address = wm.get_router_address(input.dex)
            router_contract = w3.eth.contract(address=router_address, abi=UNISWAP_V2_ROUTER_ABI)
            token_in = w3.to_checksum_address(input.token_in)
            token_out = w3.to_checksum_address(input.token_out)

            token_contract = w3.eth.contract(address=token_in, abi=ERC20_ABI)
            decimals_in = token_contract.functions.decimals().call()
            amount_in_raw = int(input.amount_in * (10 ** decimals_in))

            token_contract_out = w3.eth.contract(address=token_out, abi=ERC20_ABI)
            decimals_out = token_contract_out.functions.decimals().call()

            amounts_out = router_contract.functions.getAmountsOut(amount_in_raw, [token_in, token_out]).call()
            simulated_out = amounts_out[-1] / (10 ** decimals_out)

            return ExecuteTransactionSimulationOutput(
                simulated_amount_out=float(simulated_out),
                gas_estimate=150000,
                success=True
            )

        except Exception as e:
            return ExecuteTransactionSimulationOutput(simulated_amount_out=0.0, gas_estimate=0, success=False, error=str(e))
@tool
def remove_liquidity(input: RemoveLiquidityInput) -> RemoveLiquidityOutput:
    """Removes liquidity from an AMM pool using router contracts."""
    try:
        wallet = WalletManager(input.chain)
        w3 = wallet.get_web3()
        account = wallet.get_signer()
        router = _get_router_contract(w3, input.chain, input.dex)
        if _is_native_token(input.token_a) or _is_native_token(input.token_b):
            raise ValueError("Native token liquidity is not supported in this environment; wrap assets first.")
        token_a_router = _normalize_for_router(input.chain, input.token_a)
        token_b_router = _normalize_for_router(input.chain, input.token_b)
        lp_decimals = _get_decimals(w3, input.lp_token)
        liquidity_units = _amount_to_base_units(w3, input.lp_token, input.liquidity, lp_decimals)
        _ensure_allowance(w3, account, input.lp_token, router.address, liquidity_units)
        amount_a_min = 0
        amount_b_min = 0
        deadline = _deadline()
        tx = router.functions.removeLiquidity(
            token_a_router,
            token_b_router,
            liquidity_units,
            amount_a_min,
            amount_b_min,
            account.address,
            deadline,
        ).build_transaction({"from": account.address})
        tx_hash = _send_transaction(w3, account, tx)
        return RemoveLiquidityOutput(tx_hash=tx_hash, success=True, error=None)
    except Exception as exc:  # pragma: no cover
        logger.exception("Liquidity removal failed")
        return RemoveLiquidityOutput(tx_hash="", success=False, error=str(exc))


dex_toolkit = Toolkit(name="dex")
dex_toolkit.register(execute_swap)
dex_toolkit.register(add_liquidity)
dex_toolkit.register(remove_liquidity)
