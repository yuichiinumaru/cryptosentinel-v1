# Agent Directives (`AGENTS.md`)

**Scope:** Root directory and all subdirectories.

This document outlines the operational guidelines, coding standards, and architectural principles for all AI agents working on the CryptoSentinel project.

## 1. Project Context
CryptoSentinel is a multi-agent trading system powered by:
*   **Backend:** Python 3.10+, FastAPI, Agno (Multi-Agent Framework)
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Memory/Intelligence:** `khala-agentmemory` (SurrealDB + Vector Search)

## 2. Prime Directives (Immutable Laws)

### 2.1 The Law of Identity (AuthN vs AuthZ)
*   **Authentication (AuthN):** All API endpoints must verify `API_KEY` using `secrets.compare_digest`. No endpoints are public except `/health` and `/`.
*   **Authorization (AuthZ):** Agents operate in isolated Sessions. Global state is FORBIDDEN. Every request must instantiate a fresh Agent Team via a Factory Pattern.

### 2.2 The Law of Verification (TDD)
*   **Test-First:** No code is written without a test.
*   **Coverage:** All Tools must have unit tests.
*   **Integration:** Critical flows (Trading, Swapping) must have integration tests with mocks.

### 2.3 The Law of Preservation (Stop-Loss)
*   **Risk Management:** No trade is executed without a `Stop Loss` and `Take Profit` parameter.
*   **Asset Safety:** `approve()` calls on ERC20 tokens must be EXACT, never Infinite.
*   **Zero Trust:** All external inputs (User, API, Blockchain) are treated as malicious until validated.

## 3. Coding Standards

### 3.1 Python (Backend)
*   **Style:** Follow PEP 8.
*   **Type Hinting:** Strict type hinting is required (`mypy` compliant). No `Any` unless absolutely unavoidable.
*   **Async First:** All I/O (Database, HTTP, Blockchain) must be Asynchronous. Blocking calls are banned.
*   **Logging:** Use `logging.getLogger(__name__)`. Never use `print()`.

### 3.2 TypeScript/React (Frontend)
*   **Style:** Functional components with Hooks.
*   **Types:** Strict usage of Interfaces/Types. Avoid `any`.
*   **Security:** No API Keys in `localStorage`. Use `sessionStorage` or HttpOnly Cookies.

## 4. Operational Guidelines

1.  **Read-First:** Check `docs/02-tasks.md` for prioritized work.
2.  **Verify:** Never mark a task as complete without running the code or tests.
3.  **No Duplication:** Check `backend/tools/` before creating new tools.

## 5. Documentation Standards

*   **Source of Truth:** The `docs/` folder is the supreme authority.
*   **Structure:**
    *   `00-draft.md`: Scratchpad.
    *   `01-plan.md`: Strategic Roadmap.
    *   `02-tasks.md`: Tactical Execution List.
    *   `03-architecture.md`: System Design.
    *   `04-changelog.md`: History of Changes.
    *   `05-ideas.md`: Feature Backlog.
    *   `06-rules.md`: Specific pattern rules (e.g., .cursorrules).

### 5.1 Agent Cards (Standard Adopted from Paper 2502.01635)
*   **Mandate:** Every individual agent within the system *must* have a corresponding `AGENT_CARD.md` file in its dedicated directory (e.g., `backend/MarketAnalyst/AGENT_CARD.md`).
*   **Purpose:** This card serves as a structured, transparent, and standardized documentation of the agent's capabilities, components, and safety features.
*   **Template:** All Agent Cards must be created using the official template located at `docs/templates/agent_card_template.md`.
*   **Reference:** For a concrete example, see the `MarketAnalyst`'s card at `backend/MarketAnalyst/AGENT_CARD.md`.

## 6. External References

*   **`references/` Folder:** This directory contains external repositories added as submodules. These are to be studied for architectural patterns, strategies, and code snippets.
*   **Usage:** Code from `references/` should not be imported directly in production. Instead, analyze, adapt, and integrate it into the codebase, following CryptoSentinel's coding standards.
