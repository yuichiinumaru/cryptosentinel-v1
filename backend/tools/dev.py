import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.models import ActivityData
from backend.storage.sqlite import SqliteStorage


def _log_activity(activity_type: str, details: Dict[str, Any]) -> None:
    storage = SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))
    activity = ActivityData(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        type=activity_type,
        message=f"Developer toolkit action: {activity_type}",
        details=details,
    )
    storage.add_activity(activity)


class CodeWriterInput(BaseModel):
    task: str = Field(..., description="Task description to generate code for.")
    language: str = Field("python", description="Preferred programming language.")


class CodeWriterOutput(BaseModel):
    code: str = Field(..., description="Generated source code.")


def _generate_with_openai(prompt: str) -> str:
    from openai import OpenAI  # Lazy import to avoid dependency when unused

    client = OpenAI()
    model = os.getenv("OPENAI_CODE_MODEL", "gpt-4o-mini")
    response = client.responses.create(model=model, input=prompt, temperature=0.2)
    return response.output_text


def _generate_with_gemini(prompt: str) -> str:
    from google import genai  # Lazy import to avoid dependency when unused

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = os.getenv("GEMINI_CODE_MODEL", "gemini-1.5-pro-latest")
    result = client.responses.generate(model=model, contents=[prompt], temperature=0.2)
    return "".join(part.text for part in result.candidates[0].content.parts if hasattr(part, "text"))


def code_writer(input: CodeWriterInput) -> CodeWriterOutput:
    prompt = (
        f"Write {input.language} code to accomplish the following task:\n"
        f"{input.task}\n"
        "Return only runnable code without explanation."
    )
    provider = os.getenv("DEV_CODE_PROVIDER", "openai").lower()
    if provider == "openai":
        code = _generate_with_openai(prompt)
    elif provider == "gemini":
        code = _generate_with_gemini(prompt)
    else:
        raise ValueError(f"Unsupported code generation provider: {provider}")

    _log_activity("code_generation", {"task": input.task, "provider": provider})
    return CodeWriterOutput(code=code)


class CodeTesterInput(BaseModel):
    code: str = Field(..., description="Source code snippet to test.")


class CodeTesterOutput(BaseModel):
    success: bool = Field(..., description="Whether tests passed.")
    results: str = Field(..., description="Test output or compilation errors.")


def code_tester(input: CodeTesterInput) -> CodeTesterOutput:
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(input.code)
        tmp_path = tmp.name

    try:
        compile_proc = subprocess.run(
            ["python3", "-m", "py_compile", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if compile_proc.returncode != 0:
            _log_activity("code_test", {"status": "failed", "error": compile_proc.stderr})
            return CodeTesterOutput(success=False, results=compile_proc.stderr)

        test_command = os.getenv("DEV_TEST_COMMAND", "pytest -q").split()
        test_proc = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=300,
        )
        success = test_proc.returncode == 0
        _log_activity("code_test", {"status": "success" if success else "failed"})
        output = test_proc.stdout + test_proc.stderr
        return CodeTesterOutput(success=success, results=output)
    finally:
        os.unlink(tmp_path)


class DeployInput(BaseModel):
    command: str | None = Field(None, description="Deployment command to execute.")


class DeployOutput(BaseModel):
    success: bool = Field(..., description="Whether the deployment was successful.")
    message: str = Field(..., description="Combined stdout/stderr for the deployment command.")


def deploy(input: DeployInput) -> DeployOutput:
    command = input.command or os.getenv("DEPLOY_COMMAND")
    if not command:
        raise ValueError("Deployment command must be provided via input or DEPLOY_COMMAND environment variable.")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    success = result.returncode == 0
    message = result.stdout if success else result.stderr
    _log_activity("deployment", {"command": command, "success": success})
    return DeployOutput(success=success, message=message)


dev_toolkit = Toolkit(name="dev")
dev_toolkit.register(code_writer)
dev_toolkit.register(code_tester)
dev_toolkit.register(deploy)
