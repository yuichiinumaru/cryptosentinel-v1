import json
import os
from datetime import datetime
from typing import Dict, Any, List

import requests
from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class ComplianceCheckInput(BaseModel):
    trade_details: Dict[str, Any] = Field(..., description="The details of the trade to check.")


class ComplianceCheckOutput(BaseModel):
    is_compliant: bool = Field(..., description="Whether the trade is compliant.")
    reasons: List[str] = Field(default_factory=list, description="Reasons if the trade is not compliant.")
    required_actions: List[str] = Field(default_factory=list, description="Actions needed to remediate issues.")


def compliance_check(input: ComplianceCheckInput) -> ComplianceCheckOutput:
    trade = input.trade_details
    reasons: List[str] = []
    actions: List[str] = []

    max_notional = float(os.getenv("COMPLIANCE_MAX_NOTIONAL_USD", "500000"))
    notional = float(trade.get("notional_usd", 0))
    if notional > max_notional:
        reasons.append(f"Trade notional ${notional:,.2f} exceeds limit ${max_notional:,.2f}")
        actions.append("Seek senior approval for large notional trades")

    restricted_tokens = {token.strip().lower() for token in os.getenv("COMPLIANCE_RESTRICTED_TOKENS", "").split(",") if token.strip()}
    asset = str(trade.get("symbol") or trade.get("token", "")).lower()
    if asset and asset in restricted_tokens:
        reasons.append(f"Asset {asset} is on the restricted list")
        actions.append("Reject trade or obtain compliance waiver")

    sanctioned_addresses = {addr.strip().lower() for addr in os.getenv("COMPLIANCE_SANCTIONED_ADDRESSES", "").split(",") if addr.strip()}
    for counterparty in trade.get("counterparties", []):
        if counterparty.lower() in sanctioned_addresses:
            reasons.append(f"Counterparty {counterparty} is sanctioned")
            actions.append("Block wallet and file SAR")

    account_id = trade.get("account_id") or trade.get("portfolio_id")
    if account_id:
        storage = _get_storage()
        kyc_record = storage.get_state_value("compliance", f"kyc::{account_id}")
        if not kyc_record or kyc_record.get("status") != "approved":
            reasons.append(f"Account {account_id} lacks approved KYC")
            actions.append("Complete KYC verification for the account")

    return ComplianceCheckOutput(is_compliant=not reasons, reasons=reasons, required_actions=actions)


class CalculateFeesInput(BaseModel):
    trade_details: Dict[str, Any] = Field(..., description="The details of the trade.")


class CalculateFeesOutput(BaseModel):
    fees: float = Field(..., description="The calculated fees for the trade.")
    currency: str = Field("USD", description="Currency of the calculated fee.")
    basis_points: float = Field(..., description="Fee rate used in basis points.")


def calculate_fees(input: CalculateFeesInput) -> CalculateFeesOutput:
    fee_bps = float(os.getenv("TRADE_FEE_BPS", "12"))
    notional = float(input.trade_details.get("notional_usd", 0))
    fees = notional * fee_bps / 10000
    return CalculateFeesOutput(fees=fees, currency="USD", basis_points=fee_bps)


class GenerateFinancialReportsInput(BaseModel):
    limit: int = Field(500, description="Number of recent trades to include in the report.")


class GenerateFinancialReportsOutput(BaseModel):
    report: str = Field(..., description="The generated financial report in JSON format.")


def generate_financial_reports(input: GenerateFinancialReportsInput) -> GenerateFinancialReportsOutput:
    storage = _get_storage()
    trades = storage.get_recent_trades(limit=input.limit)
    total_notional = sum(getattr(trade, "price", 0) * getattr(trade, "amount", 0) for trade in trades)
    realized_profit = sum(getattr(trade, "profit", 0) for trade in trades)
    winners = sum(1 for trade in trades if getattr(trade, "profit", 0) > 0)
    losers = sum(1 for trade in trades if getattr(trade, "profit", 0) < 0)

    report_payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "trade_count": len(trades),
        "total_notional_usd": total_notional,
        "realized_profit_usd": realized_profit,
        "win_ratio": winners / len(trades) if trades else 0,
        "loss_ratio": losers / len(trades) if trades else 0,
    }
    return GenerateFinancialReportsOutput(report=json.dumps(report_payload, default=str))


class RegulatoryWatchInput(BaseModel):
    sources: List[str] = Field(
        default_factory=lambda: [
            "https://www.sec.gov/rss/securities-laws.xml",
            "https://www.finra.org/rss/FINRANews",
        ],
        description="RSS/JSON endpoints to poll for regulatory updates.",
    )
    limit: int = Field(5, description="Maximum number of updates to return.")


class RegulatoryWatchOutput(BaseModel):
    updates: List[str] = Field(..., description="A list of recent regulatory updates.")


def regulatory_watch(input: RegulatoryWatchInput) -> RegulatoryWatchOutput:
    updates: List[str] = []
    for source in input.sources:
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            if source.endswith(".json"):
                data = response.json()
                headlines = data.get("items", data.get("results", []))
                for item in headlines:
                    title = item.get("title") or item.get("headline")
                    if title:
                        updates.append(title)
            else:
                from xml.etree import ElementTree as ET

                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    title = item.findtext("title")
                    if title:
                        updates.append(title)
        except Exception:  # pragma: no cover - network failure
            continue
        if len(updates) >= input.limit:
            break

    if not updates:
        updates.append("No new regulatory updates detected in monitored feeds.")
    return RegulatoryWatchOutput(updates=updates[: input.limit])


compliance_toolkit = Toolkit(name="compliance")
compliance_toolkit.register(compliance_check)
compliance_toolkit.register(calculate_fees)
compliance_toolkit.register(generate_financial_reports)
compliance_toolkit.register(regulatory_watch)
