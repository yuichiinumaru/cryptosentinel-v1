from typing import Dict, Any
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field
from web3 import Web3
from backend.tools.dex import Web3Provider
import logging

logger = logging.getLogger(__name__)

# Minimal ABI for ownership check
OWNER_ABI = [{"constant":True,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"}]

class CheckSecurityInput(BaseModel):
    token_address: str = Field(..., description="The ERC20 token address.")
    chain: str = Field("ethereum", description="Blockchain network (ethereum, bsc, polygon).")

class SecurityToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="security", **kwargs)
        self.register(self.check_token_security)

    async def check_token_security(self, input: CheckSecurityInput) -> Dict[str, Any]:
        """
        Performs basic on-chain security checks (Renounced Ownership).
        Use this before trading unknown tokens.
        """
        try:
            w3 = Web3Provider.get_async_w3(input.chain)

            if not await w3.is_connected():
                return {"error": "Blockchain node not connected"}

            token_addr = w3.to_checksum_address(input.token_address)
            contract = w3.eth.contract(address=token_addr, abi=OWNER_ABI)

            # Check Ownership
            try:
                owner = await contract.functions.owner().call()
                is_renounced = int(owner, 16) == 0
                owner_status = "Renounced (Safe)" if is_renounced else f"Owned by {owner}"
            except Exception:
                # Some tokens don't have owner() function or revert
                owner = "Unknown (Function missing or revert)"
                is_renounced = False
                owner_status = "Unknown"

            # Check Code Verified (Placeholder - Requires Etherscan API)
            # In Phase 4 we will add Etherscan check.

            return {
                "address": token_addr,
                "owner": owner,
                "is_ownership_renounced": is_renounced,
                "status": owner_status,
                "security_score": 80 if is_renounced else 40 # Simple score logic
            }

        except Exception as e:
            logger.error(f"Security check failed: {e}")
            return {"error": str(e)}
