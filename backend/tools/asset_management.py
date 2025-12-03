import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.models import ActivityData
from backend.storage.sqlite import SqliteStorage
from backend.tools.dex import WalletManager

try:  # Optional dependency
    from web3 import Web3
except ImportError:  # pragma: no cover - optional dependency may be absent
    Web3 = None


BLOCK_EXPLORERS: Dict[str, Dict[str, str]] = {
    "ethereum": {"base_url": "https://api.etherscan.io/api", "api_key_env": "ETHERSCAN_API_KEY"},
    "bsc": {"base_url": "https://api.bscscan.com/api", "api_key_env": "BSCSCAN_API_KEY"},
    "polygon": {"base_url": "https://api.polygonscan.com/api", "api_key_env": "POLYGONSCAN_API_KEY"},
}

ERC20_ABI = [
    {
        "name": "decimals",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
    },
    {
        "name": "transfer",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "recipient", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
]


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


def _require_web3() -> None:
    if Web3 is None:  # pragma: no cover - optional dependency
        raise ImportError("web3 package is required for wallet transfers")


def _fetch_transactions(chain: str, address: str, limit: int = 20) -> List[Dict[str, Any]]:
    config = BLOCK_EXPLORERS.get(chain.lower())
    if not config:
        raise ValueError(f"Unsupported chain for monitoring: {chain}")

    api_key = os.getenv(config["api_key_env"], "")
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key,
    }
    response = requests.get(config["base_url"], params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") not in {"1", 1}:
        message = payload.get("message", "Unable to retrieve transactions")
        raise RuntimeError(message)

    transactions: List[Dict[str, Any]] = []
    for tx in payload.get("result", [])[:limit]:
        value_eth = float(int(tx.get("value", "0")) / 1e18)
        direction = "out" if tx.get("from", "").lower() == address.lower() else "in"
        transactions.append(
            {
                "hash": tx.get("hash"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": value_eth,
                "gas_used": int(tx.get("gasUsed", tx.get("gas", 0)) or 0),
                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", "0")), tz=timezone.utc).isoformat(),
                "direction": direction,
                "status": "success" if tx.get("isError", "0") == "0" else "failed",
            }
        )
    return transactions


class MonitorTransactionsInput(BaseModel):
    wallet_address: str = Field(..., description="The wallet address to monitor.")
    chain: str = Field("ethereum", description="Blockchain network to inspect.")


class MonitorTransactionsOutput(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="A list of recent transactions.")


def monitor_transactions(input: MonitorTransactionsInput) -> MonitorTransactionsOutput:
    transactions = _fetch_transactions(input.chain, input.wallet_address)
    return MonitorTransactionsOutput(transactions=transactions)


class CheckWalletSecurityInput(BaseModel):
    wallet_address: str = Field(..., description="The wallet address to check.")
    chain: str = Field("ethereum", description="Blockchain network to inspect.")


class CheckWalletSecurityOutput(BaseModel):
    is_secure: bool = Field(..., description="Whether the wallet is considered secure.")
    reasons: List[str] = Field(default_factory=list, description="Reasons if the wallet is not secure.")


def check_wallet_security(input: CheckWalletSecurityInput) -> CheckWalletSecurityOutput:
    reasons: List[str] = []
    transactions = _fetch_transactions(input.chain, input.wallet_address, limit=50)

    blacklisted = {addr.strip().lower() for addr in os.getenv("WALLET_RISKY_ADDRESSES", "").split(",") if addr.strip()}
    large_threshold = float(os.getenv("ASSET_LARGE_TX_THRESHOLD", "250"))

    for tx in transactions:
        counterparty = tx["to"].lower() if tx["direction"] == "out" else tx["from"].lower()
        if blacklisted and counterparty in blacklisted:
            reasons.append(f"Interaction with blacklisted address {counterparty} in {tx['hash']}")
        if tx["direction"] == "out" and tx["value"] >= large_threshold:
            reasons.append(f"Detected large outflow of {tx['value']:.4f} native tokens in {tx['hash']}")
        if tx["status"] != "success":
            reasons.append(f"Failed transaction detected: {tx['hash']}")

    recent_cutoff = datetime.utcnow().timestamp() - 3600
    recent_count = sum(1 for tx in transactions if datetime.fromisoformat(tx["timestamp"]).timestamp() >= recent_cutoff)
    frequency_threshold = int(os.getenv("ASSET_TX_FREQUENCY_THRESHOLD", "30"))
    if recent_count > frequency_threshold:
        reasons.append(f"High transaction frequency detected ({recent_count} tx in the last hour).")

    return CheckWalletSecurityOutput(is_secure=not reasons, reasons=reasons)


class SystemMonitoringInput(BaseModel):
    chains: Optional[List[str]] = Field(None, description="Specific chains to verify.")


class SystemMonitoringOutput(BaseModel):
    status: str = Field(..., description="Overall system status (healthy/degraded/outage).")
    details: Dict[str, Any] = Field(..., description="Component level diagnostics.")


def system_monitoring(input: Optional[SystemMonitoringInput] = None) -> SystemMonitoringOutput:
    details: Dict[str, Any] = {}
    unhealthy: List[str] = []

    # Storage check
    try:
        storage = _get_storage()
        storage.get_recent_activities(limit=1)
        details["storage"] = {"status": "healthy"}
    except Exception as exc:  # pragma: no cover - storage issue
        details["storage"] = {"status": "error", "error": str(exc)}
        unhealthy.append("storage")

    chains = input.chains if input and input.chains else os.getenv("MONITORED_CHAINS", "ethereum").split(",")
    chains = [chain.strip().lower() for chain in chains if chain.strip()]
    rpc_results = {}
    for chain in chains:
        rpc_url = os.getenv(f"{chain.upper()}_RPC_URL")
        if not rpc_url:
            rpc_results[chain] = {"status": "skipped", "reason": "RPC URL not configured"}
            continue
        try:
            _require_web3()
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            rpc_results[chain] = {"status": "healthy", "latest_block": w3.eth.block_number}
        except Exception as exc:  # pragma: no cover - RPC failure
            rpc_results[chain] = {"status": "error", "error": str(exc)}
            unhealthy.append(f"rpc::{chain}")
    details["rpc"] = rpc_results

    health_url = os.getenv("ZEROX_HEALTHCHECK_URL") or "https://api.0x.org/swap/v1/tokens"
    try:
        resp = requests.get(health_url, timeout=10)
        resp.raise_for_status()
        details["aggregator"] = {"status": "healthy", "endpoint": health_url}
    except Exception as exc:  # pragma: no cover - network failure
        details["aggregator"] = {"status": "error", "error": str(exc), "endpoint": health_url}
        unhealthy.append("aggregator")

    if not unhealthy:
        overall = "healthy"
    elif len(unhealthy) == 1:
        overall = "degraded"
    else:
        overall = "outage"

    return SystemMonitoringOutput(status=overall, details=details)


class SecureTransferInput(BaseModel):
    from_wallet: str = Field(..., description="The wallet to transfer from (must match signer).")
    to_wallet: str = Field(..., description="The wallet to transfer to.")
    amount: float = Field(..., description="Amount to transfer in human units.")
    chain: str = Field("ethereum", description="Blockchain network for the transfer.")
    token_address: Optional[str] = Field(None, description="ERC20 token address; leave empty for native coin.")


class SecureTransferOutput(BaseModel):
    success: bool = Field(..., description="Whether the transfer was successful.")
    tx_hash: Optional[str] = Field(None, description="Transaction hash if successful.")
    error: Optional[str] = Field(None, description="Error information if the transfer failed.")


def secure_transfer(input: SecureTransferInput) -> SecureTransferOutput:
    try:
        _require_web3()
        storage = _get_storage()
        wallet = WalletManager(input.chain)
        w3 = wallet.get_web3()
        account = wallet.get_signer()

        if account.address.lower() != input.from_wallet.lower():
            raise PermissionError("Configured signer does not control the specified from_wallet.")

        if input.token_address:
            contract = w3.eth.contract(address=Web3.to_checksum_address(input.token_address), abi=ERC20_ABI)
            decimals = contract.functions.decimals().call()
            amount_units = int(Decimal(str(input.amount)) * (10 ** decimals))
            tx = contract.functions.transfer(
                Web3.to_checksum_address(input.to_wallet),
                amount_units,
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": w3.eth.get_transaction_count(account.address),
                    "gasPrice": w3.eth.gas_price,
                }
            )
        else:
            value = Web3.to_wei(input.amount, "ether")
            tx = {
                "from": account.address,
                "to": Web3.to_checksum_address(input.to_wallet),
                "value": value,
                "gasPrice": w3.eth.gas_price,
                "nonce": w3.eth.get_transaction_count(account.address),
                "chainId": w3.eth.chain_id,
            }

        tx.setdefault("gas", int(w3.eth.estimate_gas(tx) * 1.2))
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1:
            raise RuntimeError("Transfer transaction reverted")

        storage.add_activity(
            ActivityData(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                type="secure_transfer",
                message=f"Transfer initiated to {input.to_wallet}",
                details={
                    "chain": input.chain,
                    "token": input.token_address or "native",
                    "amount": input.amount,
                    "tx_hash": tx_hash.hex(),
                },
            )
        )

        return SecureTransferOutput(success=True, tx_hash=tx_hash.hex(), error=None)
    except Exception as exc:
        return SecureTransferOutput(success=False, tx_hash=None, error=str(exc))


class FetchSecretInput(BaseModel):
    secret_name: str = Field(..., description="The name of the secret to fetch.")


class FetchSecretOutput(BaseModel):
    secret_value: str = Field(..., description="The value of the secret.")
    source: str = Field(..., description="Where the secret was retrieved from (env or storage).")


def fetch_secret(input: FetchSecretInput) -> FetchSecretOutput:
    storage = _get_storage()
    stored = storage.get_state_value("secrets", input.secret_name)
    if stored and "value" in stored:
        return FetchSecretOutput(secret_value=stored["value"], source="storage")
    env_value = os.getenv(input.secret_name)
    if env_value:
        return FetchSecretOutput(secret_value=env_value, source="env")
    raise KeyError(f"Secret '{input.secret_name}' not found in storage or environment")


asset_management_toolkit = Toolkit(name="asset_management")
asset_management_toolkit.register(monitor_transactions)
asset_management_toolkit.register(check_wallet_security)
asset_management_toolkit.register(system_monitoring)
asset_management_toolkit.register(secure_transfer)
asset_management_toolkit.register(fetch_secret)
class AssetManagementToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="asset_management", tools=[
            self.monitor_transactions,
            self.check_wallet_security,
            self.system_monitoring,
            self.secure_transfer,
            self.fetch_secret,
        ], **kwargs)

    def monitor_transactions(self, input: MonitorTransactionsInput) -> MonitorTransactionsOutput:
        """
        Monitors transactions for a given wallet address.
        """
        # ... (Placeholder implementation)
        return MonitorTransactionsOutput(transactions=[{"hash": "0xabc...", "from": "0x123...", "to": input.wallet_address}])

    def check_wallet_security(self, input: CheckWalletSecurityInput) -> CheckWalletSecurityOutput:
        """
        Checks the security of a wallet.
        """
        # ... (Placeholder implementation)
        return CheckWalletSecurityOutput(is_secure=True)

    def system_monitoring(self) -> SystemMonitoringOutput:
        """
        Monitors the overall system health.
        """
        # ... (Placeholder implementation)
        return SystemMonitoringOutput(status="OK")

    def secure_transfer(self, input: SecureTransferInput) -> SecureTransferOutput:
        """
        Performs a secure transfer of funds between wallets.
        """
        # ... (Placeholder implementation)
        return SecureTransferOutput(success=True, tx_hash="0xdef...")

    def fetch_secret(self, input: FetchSecretInput) -> FetchSecretOutput:
        """
        Fetches a secret from a secure vault.
        """
        # ... (Placeholder implementation)
        return FetchSecretOutput(secret_value="supersecret")

asset_management_toolkit = AssetManagementToolkit()
