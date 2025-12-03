# Pre-Trade Simulation (Sandwich Detection)

## Description
Before executing a swap on a DEX, the system must simulate the transaction to ensure the outcome matches expectations and to detect potential sandwich attacks (high slippage).

## Implementation Details
- **Tool**: `ExecuteTransactionSimulationTool` (or internal logic in `ExecuteSwap`).
- **Method**: Use `web3.eth.call` (or similar RPC simulation method) to simulate the swap transaction against the current block state.
- **Checks**:
    - Verify `amount_out` matches the expected minimum.
    - Check for excessive slippage which might indicate a sandwich attack in progress or low liquidity.
- **Action**: If simulation fails or shows bad execution, abort the trade.
