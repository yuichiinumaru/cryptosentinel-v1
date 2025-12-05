# The Grimoire of Resurrection

**Necromancer:** The Senior Architect
**Date:** 2024-05-22
**Objective:** Purify the codebase. Eliminate fragility.

## 💀 Rite of Resurrection: `backend/main.py` - [Fake Auth Bypass]

**The Rot (Original Sin):**
> "The function validates the *format* of the key but never checks if the key is *valid*."
> `return api_key` (Line 59)

**The Purification Strategy:**
We replace the "Security Theater" with **Zero Trust Authentication**.
1.  **Environment-Backed Validation:** The valid API key hash is loaded from the environment on startup.
2.  **Constant-Time Comparison:** Use `secrets.compare_digest` to prevent timing attacks.
3.  **Fail Loudly:** If the header is missing or invalid, we do not return 401. We return 401 with a specific error code, but we log the attempt as a security event.

**The Immortal Code:**

```python
import secrets
import os
import hashlib
from fastapi import Header, HTTPException, status
from functools import lru_cache

class SecurityConfig:
    """
    Immutable security configuration.
    Guards against empty or weak secrets.
    """
    def __init__(self):
        self._api_key = os.getenv("API_KEY")
        if not self._api_key or len(self._api_key) < 32:
            raise ValueError("FATAL: API_KEY env var missing or too weak (min 32 chars).")
        # Store hash in memory to avoid keeping plain text key if possible,
        # or just compare directly if simple. For this Rite, we compare directly
        # but safely.

    def validate(self, input_key: str) -> bool:
        return secrets.compare_digest(self._api_key, input_key)

@lru_cache()
def get_security_config() -> SecurityConfig:
    return SecurityConfig()

async def get_api_key(
    authorization: str = Header(..., description="Bearer <API_KEY>"),
    config: SecurityConfig = Depends(get_security_config)
) -> str:
    """
    Verifies the API Key using constant-time comparison.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use 'Bearer <key>'."
        )

    token = authorization.split(" ")[1]
    if not config.validate(token):
        # Log this intrusion attempt here!
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key."
        )

    return token
```

**Verification Spell:**
`curl -H "Authorization: Bearer WRONG_KEY" http://localhost:8000/status` -> Must return 401. Process must crash if `API_KEY` is unset.

---

## 💀 Rite of Resurrection: `backend/agents.py` - [Global Shared State]

**The Rot (Original Sin):**
> "Singleton agent team leaks user context. All users share the same conversation context."
> `crypto_trading_team = Team(...)` (Line 47)

**The Purification Strategy:**
We destroy the Singleton.
1.  **Factory Pattern:** Create a `Team` instance *per request*.
2.  **Session Isolation:** Require a `session_id` (derived from the user's API key or a separate header) to scope memory.
3.  **Ephemeral State:** The Team object is lightweight; the *memory* is persistent (DB).

**The Immortal Code:**

```python
from agno.agent import Agent
from agno.team.team import Team
from typing import List

# ... Agent Definitions ...

def create_user_team(session_id: str) -> Team:
    """
    Constructs a fresh Team instance for a specific user session.
    Ensures total isolation of context.
    """
    if not session_id:
        raise ValueError("Session ID cannot be empty.")

    # Re-instantiating agents is cheap if they are stateless.
    # If Agents hold state, they must also be factories.
    # Assuming Agents are stateless tool-wrappers:

    return Team(
        members=[
            deep_trader_manager,
            # ... other agents ...
        ],
        name=f"CryptoSentinelTeam-{session_id}",
        session_id=session_id,  # Agno uses this for memory scoping
        model=Config.get_model(),
        storage=get_storage()   # Shared DB, but scoped by session_id
    )
```

**Verification Spell:**
Run two concurrent requests with different session IDs. Verify that User A's "My name is Alice" is NOT retrievable by User B.

---

## 💀 Rite of Resurrection: `backend/storage/sqlite.py` - [Financial Precision Loss]

**The Rot (Original Sin):**
> "Casting `Decimal` to `float` (REAL) destroys monetary accuracy."
> `amount REAL` (Line 186)

**The Purification Strategy:**
We banish `FLOAT` from financial columns.
1.  **Storage Type:** Use `TEXT` (string) for exact Decimal representation in SQLite.
2.  **ORM Handling:** SQLAlchemy `TypeDecorator` to automatically convert `Decimal` <-> `str`.
3.  **Validation:** Ensure no `float` ever touches the money.

**The Immortal Code:**

```python
from sqlalchemy.types import TypeDecorator, TEXT
from decimal import Decimal

class SafeDecimal(TypeDecorator):
    """
    Stores Decimals as strings to prevent floating-point corruption.
    """
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, float):
             raise ValueError("CRITICAL: Attempted to save FLOAT as MONEY. Abort.")
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Decimal(value)

# Table Definition Update
"""
CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    amount TEXT NOT NULL,  -- Was REAL
    price TEXT NOT NULL,   -- Was REAL
    ...
);
"""
```

**Verification Spell:**
Store `Decimal('0.1') + Decimal('0.2')`. Retrieve it. Assert it equals `Decimal('0.3')` exactly, not `0.30000000000000004`.

---

## 💀 Rite of Resurrection: `backend/tools/dex.py` - [Blocking Call & Connection Spam]

**The Rot (Original Sin):**
> "New Web3 connection per tool call."
> "`wait_for_transaction_receipt` blocks thread for minutes."

**The Purification Strategy:**
We introduce **Async IO** and **Connection Pooling**.
1.  **Singleton Provider:** Initialize `AsyncWeb3` once.
2.  **Non-Blocking Wait:** Use `await w3.eth.wait_for_transaction_receipt(...)`.
3.  **Timeout Guards:** Strict timeouts on all network calls.

**The Immortal Code:**

```python
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth
import os

class AsyncWalletManager:
    _instance = None

    @classmethod
    async def get_instance(cls, chain: str):
        # Singleton logic per chain, or global dictionary
        if not cls._instance:
             # ... init ...
             pass
        return cls._instance

    def __init__(self, rpc_url: str):
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url), modules={'eth': (AsyncEth,)})

    async def approve_token(self, token_addr: str, spender: str, amount: int):
        # ... check allowance ...
        tx_hash = await self.w3.eth.send_raw_transaction(...)

        # Non-blocking wait!
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        return receipt
```

**Verification Spell:**
Run 100 concurrent swaps. Verify the application thread does not freeze.

---

## 💀 Rite of Resurrection: `backend/tools/portfolio.py` - [N+1 Query & Loop Write]

**The Rot (Original Sin):**
> "Writes to DB for every item read inside the loop."

**The Purification Strategy:**
We vectorize the operation.
1.  **Batch Read:** Fetch all prices in one API call (already attempted, but poorly).
2.  **In-Memory Update:** Apply logic to objects in memory.
3.  **Batch Write:** Use `bulk_save_objects` or a single `UPDATE FROM VALUES` query.

**The Immortal Code:**

```python
def sync_portfolio_prices():
    storage = get_global_storage()
    positions = storage.get_all_positions() # 1 Query

    # ... Bulk fetch prices via CoinGecko ...

    updated_positions = []
    for pos in positions:
        # ... logic ...
        updated_positions.append(pos)

    # ONE Transaction, ONE Commit
    storage.bulk_upsert_positions(updated_positions)
```

**Verification Spell:**
Measure execution time for 100 positions. Should be ~200ms (API call) + 10ms (DB), not 100 * 10ms.

---

## 💀 Rite of Resurrection: `backend/tools/wallet.py` - [Silent Failure]

**The Rot (Original Sin):**
> `except Exception: return ... balance=0.0`

**The Purification Strategy:**
**Fail Loudly.**
1.  **Custom Exception:** `class BlockchainConnectionError(Exception)`.
2.  **No Swallow:** Let the agent handle the error. The agent can decide to retry or ask the user. "I cannot check your balance right now" is better than "You have $0".

**The Immortal Code:**

```python
def get_account_balance(input: GetAccountBalanceInput) -> float:
    try:
        # ... logic ...
        return float(balance)
    except Exception as e:
        logger.error(f"Failed to fetch balance: {e}")
        # Reraise as a known tool error
        raise ToolExecutionError(f"Blockchain unreachable: {str(e)}")
```

**Verification Spell:**
Disconnect internet. Run tool. Verify it raises an exception instead of returning 0.
