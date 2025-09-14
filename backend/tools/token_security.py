from pydantic import BaseModel, Field
from typing import Optional, List
from agno.tools import tool
import requests
import os
from web3 import Web3

# Simplified ERC-20 ABI for totalSupply
ERC20_ABI = '[{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'

class CheckTokenSecurityInput(BaseModel):
    token_address: str = Field(..., description="The token contract address.")
    chain: str = Field(..., description="The blockchain where the token is deployed (e.g., 'ethereum', 'bsc').")

class CheckTokenSecurityOutput(BaseModel):
    is_safe: bool = Field(..., description="Overall safety assessment.")
    total_supply: Optional[int] = Field(None, description="Total supply of the token.")
    is_contract_verified: Optional[bool] = Field(None, description="Whether the contract source code is verified.")
    rugcheck_score: Optional[int] = Field(None, description="Security score from Rugcheck.xyz.")
    reasons: List[str] = Field([], description="List of reasons if the token is not safe.")

@tool
def check_token_security(input: CheckTokenSecurityInput) -> CheckTokenSecurityOutput:
    """
    Checks the security of a token contract by verifying its total supply and using Rugcheck.xyz.
    """
    reasons = []
    is_safe = True
    total_supply = None
    is_contract_verified = None  # This would require an Etherscan/BscScan API
    rugcheck_score = None

    # 1. Check Total Supply
    try:
        rpc_url = os.getenv(f"{input.chain.upper()}_RPC_URL")
        if not rpc_url:
            raise ValueError(f"RPC_URL for chain {input.chain} not found in environment variables.")
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        contract = w3.eth.contract(address=w3.to_checksum_address(input.token_address), abi=ERC20_ABI)
        total_supply = contract.functions.totalSupply().call()
    except Exception as e:
        reasons.append(f"Could not retrieve total supply: {e}")
        is_safe = False

    # 2. Check Rugcheck.xyz
    rugcheck_api_key = os.getenv("RUGCHECK_API_KEY")
    if rugcheck_api_key:
        try:
            response = requests.get(
                f"https://api.rugcheck.xyz/v1/check/{input.chain}/{input.token_address}",
                headers={"Authorization": f"Bearer {rugcheck_api_key}"}
            )
            response.raise_for_status()
            rugcheck_data = response.json()
            rugcheck_score = rugcheck_data.get('score')
            if rugcheck_score is not None and rugcheck_score < 85:
                is_safe = False
                reasons.append(f"Low Rugcheck.xyz score: {rugcheck_score}")
        except Exception as e:
            reasons.append(f"Error calling Rugcheck.xyz API: {e}")
            is_safe = False

    return CheckTokenSecurityOutput(
        is_safe=is_safe,
        total_supply=total_supply,
        is_contract_verified=is_contract_verified,
        rugcheck_score=rugcheck_score,
        reasons=reasons,
    )
