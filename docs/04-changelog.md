# Changelog

## [0.1.0] - Resurrection Era - 2024-10-24

### Governance
- **FORGE v2 Protocol** enacted.
- `AGENTS.md` rewritten with Prime Directives.
- `docs/` hierarchy standardized (`00` to `06`).
- Legacy artifacts (`tasklist.md`, `changelog.md`) archived.

### Audits
- Performed "Hardcore Code Audit" (Phase 2).
- Performed "Forensic Code Autopsy".
- Identified critical failures in `backend/agents.py`, `backend/tools/dex.py`, and `backend/tools/asset_management.py`.

### Architecture
- Defined "Factory Pattern" for Agents to solve state leakage.
- Defined "Async-Only" mandate for Tools.

## [0.2.0] - ARTEMIS Integration - 2025-12-18
### Architecture Harvesting
- **Event:** ARTEMIS Architecture Harvesting.
- **Decision:** Adopting ARTEMIS Dynamic Prompting model to solve Static Context limitations.
- **Decision:** Implementing "Ephemerality" via `AgentSpawner` (Python-native adapter of ARTEMIS Rust Spawner).
- **Added:** `docs/00-draft.md` (Research), `docs/01-plan.md` (Strategy), `docs/02-tasks.md` (Roadmap).
