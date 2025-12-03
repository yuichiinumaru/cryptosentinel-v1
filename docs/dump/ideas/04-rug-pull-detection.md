# Rug Pull Detection (Hybrid)

## Description
A comprehensive security check to identify malicious tokens (honeypots, rug pulls) before considering them for trading.

## Implementation Details
- **Hybrid Approach**: Combine external APIs with internal on-chain checks.
- **External APIs**:
    - **GoPlus Security API**: Check for honeypot status, tax rates, ownership renouncement.
    - **Rugcheck.xyz**: Alternative or complementary source.
- **On-Chain Checks (web3.py)**:
    - Verify `totalSupply`.
    - (Optional) Check `num_holders` and verification status (requires Indexer/Explorer API).
- **Process**: `MarketAnalyst` runs `CheckTokenSecurity` tool. If any red flag is found, the token is rejected and potentially added to a blacklist.
