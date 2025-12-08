# Task List

## 1. Core Development
- [x] Initial project setup
- [x] Define agent roles and responsibilities
- [x] Implement core agent classes
- [x] Implement tools for market data, token security, and trading
- [x] Write unit tests for each agent and tool
- [x] Write integration tests for the core agents (in progress)

## 2. Refactoring & Fixes
- [x] **Fix:** Resolve class redefinition in `backend/tools/strategy.py`
- [x] **Refactor:** Standardize agent model initialization to reduce redundancy
- [ ] **Cleanup:** Address "TODO" comments in `packages/khala-agentmemory`

## 3. Frontend & UI
- [ ] Implement a simple UI for monitoring the bot (Partial)
- [x] **Test:** Add unit/integration tests for Frontend components (Dashboard, AgentStatus)
- [ ] **Feature:** Visualize `khala-agentmemory` Knowledge Graph (Strategy 56)

## 4. Integration & Deployment
- [ ] Add `khala-agentmemory` as a submodule (Done/In-Tree)
- [ ] Deploy the bot to a cloud environment
- [x] **Docs:** Create root `AGENTS.md`
- [x] **Docs:** Update `README.md` to reflect current architecture

## 5. Critical Architecture Hardening (The Necromancer's Plan)
- [x] **Security:** Implement Zero Trust Authentication (API Key Hash) in `backend/main.py`.
- [x] **Concurrency:** Fix Global Shared State by implementing Team Factory in `backend/agents.py`.
- [x] **Data:** Implement `SafeDecimal` and WAL mode in `backend/storage/sqlite.py`.
- [x] **Quality:** Fix silent failures and duplicates in `backend/tools/wallet.py`.
- [ ] **DEX:** Refactor `backend/tools/dex.py` to use `AsyncWeb3` and singleton provider (Rite 5).
- [ ] **DEX:** Externalize `NATIVE_TOKEN_SENTINEL` and gas configs (Rite 6).
- [ ] **Portfolio:** Fix N+1 Query issue in `backend/tools/portfolio.py` (Rite 7).
- [ ] **Frontend:** Implement Full Cookie Auth (requires Backend `/login` endpoint) to replace sessionStorage.
