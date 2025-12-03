import json
import os
import re
from collections import Counter
from typing import Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class AnalyzeDocumentInput(BaseModel):
    document_path: str = Field(..., description="Absolute path to the document to analyze.")


class AnalyzeDocumentOutput(BaseModel):
    analysis: Dict[str, Any] = Field(..., description="Extracted document insights.")


def _read_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".txt", ".md", ".log"}:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    if ext == ".json":
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            data = json.load(handle)
            return json.dumps(data, indent=2)
    if ext == ".pdf":
        try:
            from langchain.document_loaders import PyPDFLoader
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ValueError("PDF analysis requires langchain with PyPDF support installed.") from exc
        loader = PyPDFLoader(path)
        pages = loader.load()
        return "\n".join(page.page_content for page in pages)
    raise ValueError(f"Unsupported document type: {ext}")


def _summarize_text(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"\s+", " ", text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned) if cleaned else []
    summary = " ".join(sentences[:3]) if sentences else ""
    words = re.findall(r"[A-Za-z0-9_]+", text.lower())
    word_count = len(words)
    keywords = [word for word, _ in Counter(words).most_common(10)]
    return {"summary": summary, "word_count": word_count, "keywords": keywords}


def analyze_document(input: AnalyzeDocumentInput) -> AnalyzeDocumentOutput:
    text = _read_text_from_file(input.document_path)
    analysis = _summarize_text(text)
    analysis["path"] = input.document_path
    return AnalyzeDocumentOutput(analysis=analysis)


document_analysis_toolkit = Toolkit(name="document_analysis")
document_analysis_toolkit.register(analyze_document)
