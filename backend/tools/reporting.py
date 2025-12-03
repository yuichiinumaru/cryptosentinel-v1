import datetime
import json
from typing import Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class GenerateReportInput(BaseModel):
    data: Dict[str, Any] = Field(..., description="Structured payload to include in the report.")
    report_type: str = Field("performance", description="Type of report to render (performance, raw, etc.).")


class GenerateReportOutput(BaseModel):
    report: str = Field(..., description="Generated Markdown report.")


def _format_performance_report(payload: Dict[str, Any]) -> str:
    lines = ["# Performance Report", f"Generated at: {datetime.datetime.utcnow().isoformat()}\n"]
    metrics = payload.get("metrics", {})
    if metrics:
        lines.append("## Key Metrics")
        for key, value in metrics.items():
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        lines.append("")

    trades = payload.get("trades") or []
    if trades:
        lines.append("## Recent Trades")
        lines.append("| ID | Symbol | Action | Amount | Price | Profit |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for trade in trades[:10]:
            lines.append(
                f"| {trade.get('id')} | {trade.get('token')} | {trade.get('action')} | "
                f"{trade.get('amount')} | {trade.get('price')} | {trade.get('profit')} |"
            )
        lines.append("")

    lines.append("## Raw Data")
    lines.append("```json")
    lines.append(json.dumps(payload, indent=2, default=str))
    lines.append("```")
    return "\n".join(lines)


def generate_report(input: GenerateReportInput) -> GenerateReportOutput:
    if input.report_type == "performance":
        report = _format_performance_report(input.data)
    else:
        report = json.dumps(input.data, indent=2, default=str)
    return GenerateReportOutput(report=report)

class ReportingToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="reporting", tools=[self.generate_report], **kwargs)

    def generate_report(self, input: GenerateReportInput) -> GenerateReportOutput:
        """
        Generates a report based on the given data.
        """
        # ... (Placeholder implementation)
        return GenerateReportOutput(report=f"This is a {input.report_type} report.")

reporting_toolkit = ReportingToolkit()
