# CryptoSentinel - Autonomous Cryptocurrency Trading Bot

## 1. Project Overview

CryptoSentinel is an advanced, autonomous trading bot for cryptocurrencies. It utilizes a sophisticated multi-agent AI framework to analyze market data, execute trades, and continuously learn. The system features a **Memory-Centric Architecture** powered by `khala-agentmemory`, enabling long-term reasoning and strategy evolution.

## 2. Architecture

The system is composed of three main pillars:

### 2.1. Backend (`backend/`)
*   **Framework:** FastAPI + Agno (formerly Phidata).
*   **Agents:** 12 specialized AI agents (e.g., `MarketAnalyst`, `Trader`, `RiskAnalyst`).
*   **Tools:** Over 130 tools for analysis, execution, and research.

### 2.2. Frontend (`src/`)
*   **Stack:** React, TypeScript, Vite, Tailwind CSS.
*   **Features:** Real-time dashboard, agent activity monitoring, and manual overrides.

### 2.3. Intelligence Engine (`packages/khala-agentmemory/`)
*   **Core:** SurrealDB-based memory system.
*   **Strategies:** Implements ~115 of 170 planned strategies, including:
    *   Vector & Hybrid Search (RRF).
    *   Graph Knowledge Base.
    *   Prompt Optimization (PromptWizard).
    *   Multi-Agent Coordination protocols.

## 3. Getting Started

### 3.1. Prerequisites
*   Python 3.10+
*   Node.js 18+
*   SurrealDB (Local or Cloud)

### 3.2. Backend Setup
```bash
# Install khala-memory in editable mode
pip install -e packages/khala-agentmemory

cd backend
pip install -r requirements.txt
# Configure .env (see deployment_guide.md)
uvicorn main:app --reload
```

### 3.3. Frontend Setup
```bash
npm install
npm run dev
```

## 4. Documentation
*   **Assessment:** See `docs/codebase_assessment.md` for a detailed audit of the current state.
*   **Strategies:** See `packages/khala-agentmemory/docs/06-strategies-master.md` for the full list of 170 strategies.
*   **Agents:** See `AGENTS.md` for development guidelines.

## 5. Contributing
Please refer to `tasklist.md` for current priorities. All contributions must include tests.

## 6. License
MIT License.
