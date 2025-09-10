import os
import requests
from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools import tool
from web3 import Web3


class CheckTokenSecurityInput(BaseModel):
    token_address: str = Field(..., description="The address of the token contract.")
    chain: str = Field("ethereum", description="The blockchain to check the token on.")


class CheckTokenSecurityOutput(BaseModel):
    is_safe: bool = Field(..., description="Whether the token is considered safe.")
    details: Dict[str, Any] = Field(..., description="A dictionary containing the security details.")
    reasons: str = Field(..., description="A summary of the reasons for the safety assessment.")


@tool(input_schema=CheckTokenSecurityInput, output_schema=CheckTokenSecurityOutput)
def CheckTokenSecurity(token_address: str, chain: str = "ethereum") -> Dict[str, Any]:
    """
    Checks the security of a token contract against rug pulls, honeypots, etc.
    """
    goplus_api_key = os.getenv("GOPLUS_API_KEY")
    rugcheck_api_key = os.getenv("RUGCHECK_API_KEY")
    infura_url = os.getenv("INFURA_URL")

    w3 = Web3(Web3.HTTPProvider(infura_url))

    details = {}
    reasons = []
    is_safe = True

    # Basic on-chain checks
    try:
        token_address = w3.to_checksum_address(token_address)
        contract = w3.eth.contract(address=token_address, abi=[{"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}])
        total_supply = contract.functions.totalSupply().call()
        details["total_supply"] = total_supply
    except Exception as e:
        is_safe = False
        reasons.append(f"On-chain check failed: {e}")
        details["on_chain_check"] = f"Failed: {e}"

    # GoPlus Security
    if goplus_api_key:
        try:
            url = f"https://api.gopluslabs.io/api/v1/token_security/{chain}?contract_addresses={token_address}"
            headers = {"X-API-KEY": goplus_api_key}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            details["goplus"] = data
            if data.get("result", {}).get(token_address.lower(), {}).get("is_honeypot") == "1":
                is_safe = False
                reasons.append("GoPlus detected a honeypot.")
        except Exception as e:
            details["goplus"] = f"Failed to fetch data: {e}"

    # Rugcheck.xyz
    if rugcheck_api_key:
        try:
            url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
            headers = {"X-API-KEY": rugcheck_api_key}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            details["rugcheck"] = data
            if data.get("risks", []):
                is_safe = False
                reasons.append("Rugcheck detected risks.")
        except Exception as e:
            details["rugcheck"] = f"Failed to fetch data: {e}"

    return {
        "is_safe": is_safe,
        "details": details,
        "reasons": " ".join(reasons) if reasons else "No immediate risks found."
    }
