# Event Sourcing & Audit

## Description
Persist all state changes as a sequence of immutable events to ensure full auditability and the ability to "replay" the system state.

## Implementation Details
- **Concept**: Instead of just storing "Current Price = 100", store "PriceUpdated(100) at 10:00".
- **Benefits**:
    - Debugging: Trace exactly why an agent made a decision.
    - Compliance: Full audit trail of all actions and market conditions at the time of trade.
- **Storage**: Append-only `events` log in the database.
