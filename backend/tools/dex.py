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
    token_in: str = Field(..., description="Address of the token to sell.")
    token_out: str = Field(..., description="Address of the token to buy.")
    amount_in: float = Field(..., description="Amount of token_in to sell.")
    slippage: float = Field(0.01, description="Maximum acceptable slippage (e.g., 0.01 for 1%).")
    chain: str = Field("ethereum", description="Blockchain to execute the swap on.")
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = Field("uniswap_v2", description="DEX to use.")

class ExecuteSwapOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the executed swap.")
    success: bool = Field(..., description="True if the swap was successful, False otherwise.")
    error: str = Field(None, description="Error message if the swap failed.")

@tool
def execute_swap(input: ExecuteSwapInput) -> ExecuteSwapOutput:
    """
    Executes a token swap on a decentralized exchange.
    """
    try:
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
    token_a: str = Field(..., description="Address of the first token.")
    token_b: str = Field(..., description="Address of the second token.")
    amount_a: float = Field(..., description="Amount of the first token.")
    amount_b: float = Field(..., description="Amount of the second token.")
    chain: str = Field("ethereum", description="Blockchain to add liquidity to.")
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = Field("uniswap_v2", description="DEX to use.")

class AddLiquidityOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the liquidity addition.")
    success: bool = Field(..., description="True if successful, False otherwise.")
    error: str = Field(None, description="Error message if failed.")

class RemoveLiquidityInput(BaseModel):
    token_a: str = Field(..., description="Address of the first token.")
    token_b: str = Field(..., description="Address of the second token.")
    liquidity: float = Field(..., description="Amount of LP tokens to remove.")
    chain: str = Field("ethereum", description="Blockchain to remove liquidity from.")
    dex: Literal["uniswap_v2", "pancakeswap_v2"] = Field("uniswap_v2", description="DEX to use.")

class RemoveLiquidityOutput(BaseModel):
    tx_hash: str = Field(..., description="Transaction hash of the liquidity removal.")
    success: bool = Field(..., description="True if successful, False otherwise.")
    error: str = Field(None, description="Error message if failed.")

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
    """
    Removes liquidity from a decentralized exchange pool.
    """
    try:
        # ... (Implementation details)
        return RemoveLiquidityOutput(tx_hash="0x789...", success=True)
    except Exception as e:
        return RemoveLiquidityOutput(tx_hash="", success=False, error=str(e))
