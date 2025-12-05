# The Grimoire of Fixes (The Resurrection Logs)

**Necromancer:** The Senior Architect Necromancer
**Date:** 2024-10-24
**Objective:** Purify the codebase of incompetence and enforce "Zero Fragility."

-----

## 💀 Rite of Resurrection: Backend Core - Security & Concurrency

**The Rot (Original Sin):**
> "Injecting request headers into global process state... Race conditions guarantee key leakage."
> "DuckDuckGoTools (synchronous) called inside async def. Blocks the main event loop."

**The Purification Strategy:**
*   **Security:** Removed `os.environ` mutation in `get_api_key`. Keys are validated but never injected into global state.
*   **Concurrency:** Wrapped all blocking calls (DuckDuckGo, SQLite storage, Agent execution) in `fastapi.concurrency.run_in_threadpool`.
*   **Protection:** Implemented `slowapi` rate limiting (`Limiter`) on all endpoints to prevent DoS.

**The Immortal Code:**
*(See `backend/main.py`)*

## 💀 Rite of Resurrection: Storage - Data Integrity

**The Rot (Original Sin):**
> "Sharing a single connection across an async/threaded web server without locking is guaranteed to cause database corruption."

**The Purification Strategy:**
*   **Architecture:** Replaced raw `sqlite3` connection with `SQLAlchemy` `QueuePool` and `Engine`.
*   **Thread Safety:** Each operation now acquires a fresh connection from the pool, preventing "database is locked" errors and corruption.
*   **Schema Safety:** Explicitly casts complex types (Decimal) to storage-compatible types (Float/String) to prevent encoding crashes.

**The Immortal Code:**
*(See `backend/storage/sqlite.py`)*

## 💀 Rite of Resurrection: DEX Tools - Wallet Safety

**The Rot (Original Sin):**
> "Approve(..., 2**256 - 1) grants UNLIMITED access... Swap transaction is sent immediately after Approve without waiting."

**The Purification Strategy:**
*   **Least Privilege:** Approvals are now calculated exactly for the `amount_in_wei` needed.
*   **Consistency:** Added `w3.eth.wait_for_transaction_receipt` to ensure Approval is mined before attempting Swap.
*   **Atomic Decomposition:** Refactored nonce management to refresh after approval logic.

**The Immortal Code:**
*(See `backend/tools/dex.py`)*

## 💀 Rite of Resurrection: Risk & Portfolio - Logic Restoration

**The Rot (Original Sin):**
> "The class RiskManagementToolkit overwrites the functional implementation with a version that only print()s to stdout."
> "Calls non-existent method storage.get_all_portfolio_items()."

**The Purification Strategy:**
*   **Exorcism:** Deleted the deceptive placeholder classes in `risk_management.py` and `portfolio.py`.
*   **Restoration:** Reinstated the functional standalone tools that correctly interact with the (now thread-safe) storage layer.
*   **Fix:** Corrected method calls to match the `SqliteStorage` API.

**The Immortal Code:**
*(See `backend/tools/risk_management.py` and `backend/tools/portfolio.py`)*

## 💀 Rite of Resurrection: Configuration - Zero Trust

**The Rot (Original Sin):**
> "Key rotation is a lie... Module level singleton initialized at import."

**The Purification Strategy:**
*   **True Rotation:** Implemented random selection from `gemini_api_keys`.
*   **Validation:** Crash immediately if keys are missing or invalid (`ValueError`).
*   **Cleanup:** Removed module-level `shared_model` side effect.

**The Immortal Code:**
*(See `backend/config.py`)*

## 💀 Rite of Resurrection: Protocol - Precision

**The Rot (Original Sin):**
> "Uses float for amount... Floating point arithmetic is forbidden in finance."

**The Purification Strategy:**
*   **Type Safety:** Replaced `float` with `Decimal` in `TradeOrder`, `TradeResult`, and other financial models.
*   **Immortal Math:** Ensures precision for all monetary values.

**The Immortal Code:**
*(See `backend/protocol.py`)*

## 💀 Rite of Resurrection: Agents - Clean Initialization

**The Rot (Original Sin):**
> "Storage execution at module level... Spaghetti Factory."

**The Purification Strategy:**
*   **Lazy Loading:** Wrapped storage initialization in `get_storage()`.
*   **Safe Dependency:** Updated Team to use `Config.get_model()` instead of relying on the fragile global `shared_model`.

**The Immortal Code:**
*(See `backend/agents.py`)*
