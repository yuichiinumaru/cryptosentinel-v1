# Post-Trade Approval Revocation

## Description
A mandatory security hygiene practice to revoke token allowances granted to DEX routers immediately after a swap is completed.

## Implementation Details
- **Risk**: Infinite approvals leave the wallet vulnerable if the DEX contract is compromised later.
- **Workflow**:
    1. `ExecuteSwap` grants approval (if needed) -> Executes Swap.
    2. Immediately after confirmation, trigger `RevokeApproval` (set allowance to 0).
- **Automation**: This should be automated within the `Trader`'s workflow or the `ExecuteSwap` tool itself.
