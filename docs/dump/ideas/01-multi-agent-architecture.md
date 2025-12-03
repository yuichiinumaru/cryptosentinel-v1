# Multi-Agent Architecture

## Description
The system is built on a multi-agent architecture where specialized agents collaborate to achieve the goal of autonomous trading. This replaces the monolithic bot approach. Each agent has a specific role and responsibility.

## Roles
- **MarketAnalyst**: Responsible for market intelligence, scanning for opportunities, and performing security checks (Rug Pull, Fake Volume).
- **DeepTraderManager**: Acts as the team lead, approving or rejecting trades based on risk parameters and strategy alignment.
- **Trader**: Executes the approved trades on DEXs/CEXs securely.
- **PortfolioManager**: Tracks positions, calculates performance metrics (ROI, Drawdown), and reports risk.
- **LearningCoordinator**: Analyzes historical performance to adjust agent instructions and tool parameters.

## Communication
- Agents communicate asynchronously via JSON messages.
- No hardcoded `if-then-else` logic for high-level decisions; LLM decides when to use tools.
