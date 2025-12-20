# MarketAnalyst Agent Card

## 1. Basic Information
- **Website:** N/A (Internal component of CryptoSentinel)
- **Short Description:** A specialized AI agent responsible for analyzing cryptocurrency market data to identify safe and profitable trading opportunities.
- **Intended Uses:** The agent is designed to perform market analysis, focusing on technical indicators like RSI and Bollinger Bands for high-capitalization tokens. It verifies token security and generates trade recommendations for the `DeepTraderManager`.
- **Date(s) Deployed:** 2024 (Initial deployment with the CryptoSentinel system)

## 2. Developer
- **Website:** N/A
- **Legal Name:** N/A (Internal Development Team)
- **Entity Type:** Internal Project
- **Country:** N/A
- **Safety Policies:** The agent operates under the strict safety guidelines defined in the root `AGENTS.md`, including mandatory security checks for all recommended tokens.

## 3. System Components
- **Backend Model:** Google Gemini (`gemini-1.5-flash-latest` by default, configured in `backend/agents/__init__.py`)
- **Publicly Available Model Specification:** No, the agent's behavior is defined by its instruction file at `backend/MarketAnalyst/instructions.md`.
- **Reasoning, Planning, and Memory Implementation:** The agent uses a Chain-of-Thought process for its reasoning, as mandated by its instructions. It leverages the `KhalaMemoryToolkit` for long-term memory access and contextual understanding.
- **Observation Space:** The agent can observe market data via the `MarketDataToolkit`, including prices, technical indicators, and token security information.
- **Action Space/Tools:**
  - `MarketDataToolkit`: To fetch real-time market data.
  - `KhalaMemoryToolkit`: To read from and write to the system's long-term memory.
- **User Interface:** N/A (The agent interacts with other agents, primarily the `DeepTraderManager`, not directly with end-users).
- **Development Cost and Compute:** Unknown.

## 4. Guardrails and Oversight
- **Accessibility of Components:**
  - **Weights:** N/A (Uses a proprietary backend model).
  - **Data:** N/A (Market data is fetched from external APIs).
  - **Code:** Available within the project's repository.
  - **Scaffolding:** Available within the project's repository.
  - **Documentation:** Available as `instructions.md` and this Agent Card.
- **Controls and Guardrails:** The agent has strict instructions to *never* recommend a token without a successful security check and to *only* communicate with the `DeepTraderManager`.
- **Customer and Usage Restrictions:** N/A (Internal agent).
- **Monitoring and Shutdown Procedures:** The agent operates within the FastAPI application's lifecycle and can be monitored through standard application logging. It is instantiated per-session, limiting its operational scope.

## 5. Evaluations
- **Notable Benchmark Evaluations:** None.
- **Bespoke Testing:** Internal, project-specific tests for functionality and integration.
- **Safety:** Safety is primarily enforced by its strict operational instructions, such as the mandatory use of `CheckTokenSecurity` via its toolkits.
- **Publicly Reported External Red-Teaming or Comparable Auditing:**
  - **Personnel:** None.
  - **Scope, Scale, Access, and Methods:** None.
  - **Findings:** None.

## 6. Ecosystem
- **Interoperability with Other Systems:** The agent is designed to work within the CryptoSentinel multi-agent team, primarily interacting with the `DeepTraderManager`.
- **Usage Statistics and Patterns:** Usage is tied to the overall activity of the CryptoSentinel system.

## 7. Additional Notes
- This agent is a core component of the system's "Debate" architecture, providing the primary market analysis that may be scrutinized by other specialized agents.