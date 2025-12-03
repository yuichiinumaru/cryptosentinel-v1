# Database Schema & Persistence

## Description
Use a local SQLite database to persist state, ensuring the bot can restart without losing context and providing data for analysis.

## Implementation Details
- **Technology**: SQLite.
- **Tables**:
    - `tokens`: `address` (PK), `symbol`, `chain`, `risk_score`, `is_blacklisted`, `history` (JSON).
    - `events`: `id`, `event_type` (pump, rug, etc.), `details` (JSON), `timestamp`.
    - `transactions`: `id`, `token_address`, `action`, `amount`, `tx_hash`, `timestamp`.
    - `portfolio`: `token_address` (PK), `amount`, `entry_price`.
