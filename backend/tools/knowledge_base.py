import os
from pathlib import Path
from typing import List, Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field


class KnowledgeBaseSearchInput(BaseModel):
    query: str = Field(..., description="Query string to search within the knowledge base.")
    max_results: int = Field(5, description="Maximum number of matches to return.")


class KnowledgeBaseSearchOutput(BaseModel):
    matches: List[Dict[str, Any]] = Field(..., description="Matched documents with snippets.")


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def search_knowledge_base(input: KnowledgeBaseSearchInput) -> KnowledgeBaseSearchOutput:
    base_path = Path(os.getenv("KNOWLEDGE_BASE_PATH", "docs"))
    if not base_path.exists():
        raise FileNotFoundError(f"Knowledge base path {base_path} does not exist")

    matches: List[Dict[str, Any]] = []
    lowered_query = input.query.lower()
    for file in base_path.rglob("*.md"):
        text = _load_text(file)
        if lowered_query in text.lower():
            index = text.lower().index(lowered_query)
            start = max(index - 120, 0)
            end = min(index + 120, len(text))
            snippet = text[start:end].replace("\n", " ")
            matches.append({"file": str(file), "snippet": snippet})
        if len(matches) >= input.max_results:
            break

    return KnowledgeBaseSearchOutput(matches=matches)


knowledge_base_toolkit = Toolkit(name="knowledge_base")
knowledge_base_toolkit.register(search_knowledge_base)
