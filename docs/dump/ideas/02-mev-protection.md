# MEV Protection (Flashbots)

## Description
To prevent front-running and sandwich attacks, the system must avoid sending transactions to the public mempool where they can be observed by predatory bots.

## Implementation Details
- **Flashbots Protect RPC**: Use Flashbots' private RPC endpoints to submit transactions.
- **Library**: Use the `flashbots` python library or configure `web3.py` to use the Flashbots RPC URL.
- **Benefit**: Transactions are not visible in the public mempool until they are included in a block, preventing MEV exploits.
