# Agent Directives (`AGENTS.md`)

**Scope:** Root directory and all subdirectories.

This document outlines the operational guidelines, coding standards, and architectural principles for all AI agents working on the CryptoSentinel project.

## 1. Project Context
CryptoSentinel is a multi-agent trading system powered by:
*   **Backend:** Python 3.10+, FastAPI, Agno (Multi-Agent Framework)
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Memory/Intelligence:** `khala-agentmemory` (SurrealDB + Vector Search)

## 2. Coding Standards

### 2.1 Python (Backend)
*   **Style:** Follow PEP 8.
*   **Type Hinting:** strict type hinting is required for all function arguments and return values.
*   **Testing:** All new tools and agents MUST have accompanying unit tests in `backend/tests/`.
*   **Docstrings:** Use Google-style docstrings.

### 2.2 TypeScript/React (Frontend)
*   **Style:** Functional components with Hooks.
*   **Types:** Strict usage of Interfaces/Types. Avoid `any`.
*   **Testing:** Components must be tested using Vitest/React Testing Library.

## 3. Operational Guidelines

1.  **Read-First:** Always read the `tasklist.md` and `docs/codebase_assessment.md` before starting work.
2.  **Verify:** Never mark a task as complete without running the code or tests to verify it.
3.  **Strategy Awareness:** When working on memory or reasoning, consult `packages/khala-agentmemory/docs/06-strategies-master.md` to ensure alignment with the 170-strategy roadmap.
4.  **No Duplication:** Before creating a new tool, check `backend/tools/` and `packages/khala-agentmemory/` to ensure it doesn't already exist.

## 4. Architecture Notes

*   **Agents:** Defined in `backend/agents.py`. Each agent has a specific role (e.g., `MarketAnalyst`, `Trader`).
*   **Memory:** The `khala-agentmemory` package is the source of truth for long-term memory. Use its services rather than creating ad-hoc storage where possible.
*   **Tools:** Tools are the primary way agents interact with the world. Keep them atomic and well-documented.
