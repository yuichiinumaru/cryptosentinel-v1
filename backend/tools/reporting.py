from pydantic import BaseModel, Field
from typing import Dict, Any
from agno.tools.toolkit import Toolkit
from agno.tools.function import Function

class GenerateReportInput(BaseModel):
    data: Dict[str, Any] = Field(..., description="The data to include in the report.")
    report_type: str = Field("performance", description="The type of report to generate.")

class GenerateReportOutput(BaseModel):
    report: str = Field(..., description="The generated report.")

def generate_report_func(input: GenerateReportInput) -> GenerateReportOutput:
    """
    Generates a report based on the given data.
    """
    # ... (Placeholder implementation)
    return GenerateReportOutput(report=f"This is a {input.report_type} report.")

generate_report = Function.from_callable(generate_report_func)

reporting_toolkit = Toolkit(name="reporting")
reporting_toolkit.register(generate_report)
