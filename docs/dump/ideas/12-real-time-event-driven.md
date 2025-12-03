# Real-Time Event-Driven Architecture

## Description
Shift from polling-based data fetching to an event-driven model using WebSockets for lower latency and better responsiveness.

## Implementation Details
- **Technology**: WebSockets (Python `websockets` or `aiohttp`).
- **Use Cases**:
    - Streaming market prices (CoinGecko Pro or CEX WS).
    - Mempool monitoring (Blocknative).
- **Agent Handling**: Agents or specific tools need `async` listeners that trigger actions ("events") when data arrives, rather than waiting for a cron job.
