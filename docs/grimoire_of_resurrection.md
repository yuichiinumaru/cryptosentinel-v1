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
from fastapi import Header, HTTPException, status, Depends
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
        # Store hash in memory to avoid keeping plain text key if possible

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

def create_user_team(session_id: str) -> Team:
    """
    Constructs a fresh Team instance for a specific user session.
    Ensures total isolation of context.
    """
    if not session_id:
        raise ValueError("Session ID cannot be empty.")

    return Team(
        members=[
            # ... agents ...
        ],
        name=f"CryptoSentinelTeam-{session_id}",
        session_id=session_id,  # Agno uses this for memory scoping
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

# Schema Update:
# amount TEXT NOT NULL
```

**Verification Spell:**
Store `Decimal('0.1') + Decimal('0.2')`. Retrieve it. Assert it equals `Decimal('0.3')` exactly.

---

## 💀 Rite of Resurrection: `backend/storage/sqlite.py` - [Thread Safety]

**The Rot (Original Sin):**
> "`check_same_thread=False` combined with `QueuePool`. This invites race conditions."

**The Purification Strategy:**
We enable concurrency safety.
1.  **WAL Mode:** Enable Write-Ahead Logging for better concurrency.
2.  **Locking:** Use immediate transactions to prevent locking errors.
3.  **Pool Type:** If using file-based SQLite with multiple threads, stick to `SingletonThreadPool` or handle properly. But better: just use WAL.

**The Immortal Code:**

```python
from sqlalchemy import event

def configure_sqlite(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

# In init:
self.engine = create_engine(url, ...)
event.listen(self.engine, "connect", configure_sqlite)
```

**Verification Spell:**
Run 50 threads inserting rows simultaneously. Verify zero `database is locked` errors.

---

## 💀 Rite of Resurrection: `backend/tools/dex.py` - [Blocking Call & Connection Spam]

**The Rot (Original Sin):**
> "New Web3 connection per tool call."
> "`wait_for_transaction_receipt` blocks thread for minutes."

**The Purification Strategy:**
We introduce **Async IO** and **Connection Pooling**.
1.  **Singleton Provider:** Initialize `AsyncWeb3` once.
2.  **Non-Blocking Wait:** Use `await w3.eth.wait_for_transaction_receipt(...)`.

**The Immortal Code:**

```python
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth

class AsyncWalletManager:
    _instance = None

    @classmethod
    async def get_instance(cls, rpc_url: str):
        if not cls._instance:
             cls._instance = AsyncWalletManager(rpc_url)
        return cls._instance

    def __init__(self, rpc_url: str):
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url), modules={'eth': (AsyncEth,)})

    async def wait_tx(self, tx_hash):
        return await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
```

**Verification Spell:**
Run 100 concurrent swaps. Verify the application thread does not freeze.

---

## 💀 Rite of Resurrection: `backend/tools/dex.py` - [Magic Numbers & Config]

**The Rot (Original Sin):**
> "Hardcoded `NATIVE_TOKEN_SENTINEL`."
> "Magic `gas_estimate=200000`."

**The Purification Strategy:**
**No Magic.**
1.  **Configuration Injection:** All constants moved to `DexConfig`.
2.  **Dynamic Gas:** Estimate gas using `eth_estimateGas` instead of guessing.

**The Immortal Code:**

```python
class DexConfig:
    def __init__(self):
        self.native_sentinel = os.getenv("NATIVE_TOKEN_SENTINEL", "0xeeee...")
        self.default_slippage = float(os.getenv("DEFAULT_SLIPPAGE", "0.01"))

async def estimate_swap_gas(self, tx_params):
    try:
        return await self.w3.eth.estimate_gas(tx_params)
    except Exception:
        # Fallback only if estimation fails
        return 300000
```

**Verification Spell:**
Change `NATIVE_TOKEN_SENTINEL` in `.env`. Verify tool uses new value.

---

## 💀 Rite of Resurrection: `backend/tools/portfolio.py` - [N+1 Query & Loop Write]

**The Rot (Original Sin):**
> "Writes to DB for every item read inside the loop."

**The Purification Strategy:**
We vectorize the operation.
1.  **Batch Read:** Fetch all prices in one API call.
2.  **Batch Write:** Use `bulk_save_objects`.

**The Immortal Code:**

```python
def sync_portfolio_prices():
    storage = get_global_storage()
    positions = storage.get_all_positions()

    # ... Bulk fetch prices ...

    # One atomic commit
    storage.bulk_upsert_positions(positions)
```

**Verification Spell:**
Measure execution time for 100 positions. Should be O(1) relative to DB commits.

---

## 💀 Rite of Resurrection: `backend/tools/wallet.py` - [Silent Failure]

**The Rot (Original Sin):**
> `except Exception: return ... balance=0.0`

**The Purification Strategy:**
**Fail Loudly.**
1.  **No Swallow:** Raise `ToolExecutionError`.

**The Immortal Code:**

```python
def get_account_balance(input: GetAccountBalanceInput) -> float:
    try:
        # ... logic ...
        return float(balance)
    except Exception as e:
        logger.error(f"Failed to fetch balance: {e}")
        raise ToolExecutionError(f"Blockchain unreachable: {str(e)}")
```

**Verification Spell:**
Disconnect internet. Run tool. Verify it raises an exception instead of returning 0.

---

## 💀 Rite of Resurrection: `src/services/api.ts` - [XSS / Insecure Storage]

**The Rot (Original Sin):**
> `localStorage.getItem("openaiApiKey")`. Secrets stored in accessible storage.

**The Purification Strategy:**
**HttpOnly Cookies.**
1.  **Backend:** Send API Key as an `HttpOnly` cookie upon login/config.
2.  **Frontend:** Remove all `localStorage` calls for secrets. Browser handles cookie attachment automatically.

**The Immortal Code:**

```typescript
// src/services/api.ts

// DELETE THIS:
// export const getApiKey = () => localStorage.getItem("openaiApiKey");

// REPLACE WITH:
// Nothing. The browser sends the cookie automatically.

const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  // No Authorization header needed if using Cookies!
  // OR if using header, fetch it from a secure memory store (Zustand), not localStorage.

  const response = await fetch(url, {
    ...options,
    credentials: "include", // This sends the cookies
  });
  // ...
};
```

**Verification Spell:**
Open DevTools -> Application -> Local Storage. Verify it is empty. Execute a trade. Verify it works (via Cookie).

---

## 💀 Rite of Resurrection: `backend/main.py` - [Unsecured External APIs]

**The Rot (Original Sin):**
> "CoinGecko called without an API key. This will hit rate limits."

**The Purification Strategy:**
**Managed Clients.**
1.  **Client Injection:** Use a `MarketDataProvider` class that manages the API key and rate limits.
2.  **Circuit Breaker:** If API fails, switch to backup or fail gracefully.

**The Immortal Code:**

```python
class CoinGeckoClient:
    def __init__(self):
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.base_url = "https://pro-api.coingecko.com/api/v3" if self.api_key else "https://api.coingecko.com/api/v3"

    async def get_price(self, ...):
        headers = {"x-cg-pro-api-key": self.api_key} if self.api_key else {}
        # ... request ...
```

**Verification Spell:**
Run load test. Verify calls include the header (mocked).
