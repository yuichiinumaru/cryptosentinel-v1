# MCP Integration Analysis & Evaluation

**Date:** December 2025
**Scope:** Evaluation of MCP Server inclusion for CryptoSentinel
**Reference:** Agno Documentation, User Provided MCP Audit Report

## 1. Executive Summary

The proposed integration of Model Context Protocol (MCP) servers into the CryptoSentinel architecture is **highly recommended** and technically feasible. Agno (formerly Phidata) provides native support for MCP via `agno.tools.mcp.MCPTools`, allowing for seamless integration of external tools without complex wrapper code.

We have centralized all necessary configuration keys in a new `.env` file (and `.env.example`) in the root directory, enabling immediate configuration of these services.

## 2. Architecture Alignment

The current `CryptoSentinelTeam` (defined in `backend/agents.py`) consists of specialized agents (e.g., `MarketAnalyst`, `Trader`, `ComplianceOfficer`). The recommended MCP servers align perfectly with these roles:

*   **Security & Compliance**: Aderyn MCP -> `compliance_officer` or new `SecurityAgent`.
*   **Execution**: EVM MCP -> `trader_agent`, `asset_manager`.
*   **Market Intelligence**: CoinGecko MCP -> `market_analyst`, `analista_fundamentalista`.
*   **Development**: GitHub MCP -> `dev_agent`.

## 3. Server Evaluation

### 3.1. Smart Contract Security: Aderyn MCP (Critical)
*   **Verdict:** **Adopt Immediately**.
*   **Integration:** Run via `npx` command within `MCPTools`.
*   **Role:** Enhances the `compliance_officer` agent to perform deep AST-based static analysis of contracts before interaction.
*   **Configuration:** No API key required for local CLI, but Node.js environment is needed.

### 3.2. Blockchain Execution: EVM MCP (Critical)
*   **Verdict:** **Adopt Immediately**.
*   **Integration:** Connects agents directly to 30+ chains.
*   **Role:** `trader_agent` and `asset_manager` gain capability to read/write contracts and resolve ENS without custom Python web3 boilerplate.
*   **Configuration:** Requires `ETH_RPC_URL` (added to `.env`).

### 3.3. Market Intelligence: CoinGecko MCP (High)
*   **Verdict:** **Adopt**.
*   **Integration:** Provides robust market data.
*   **Role:** `market_analyst` uses this for real-time price discovery and trend analysis.
*   **Configuration:** Requires `COINGECKO_API_KEY` (added to `.env`).

### 3.4. Infrastructure & Memory: Qdrant MCP (Medium/Conflict)
*   **Verdict:** **Evaluate with Caution**.
*   **Conflict Note:** CryptoSentinel currently uses `khala-agentmemory` powered by **SurrealDB**, which also supports vector search and graph relations.
*   **Recommendation:** Prioritize `khala-agentmemory` as the source of truth to avoid split-brain memory states. Only adopt Qdrant if SurrealDB proves insufficient for specific vector embedding needs. Introducing a second vector store adds infrastructure complexity.

### 3.5. Developer Activity: GitHub MCP (Medium)
*   **Verdict:** **Adopt**.
*   **Role:** Empowers `dev_agent` to monitor repo health and update codebase context.
*   **Configuration:** Requires `GITHUB_PERSONAL_ACCESS_TOKEN` (added to `.env`).

## 4. Integration Strategy

### Step 1: Configuration
Ensure the `.env` file is populated with the relevant keys:
```bash
COINGECKO_API_KEY=...
ETH_RPC_URL=...
GITHUB_PERSONAL_ACCESS_TOKEN=...
```

### Step 2: Code Implementation (Example)
Modify `backend/agents.py` to include `MCPTools`.

```python
import os
from agno.tools.mcp import MCPTools

# Ensure env vars are loaded
from dotenv import load_dotenv
load_dotenv()

# Define MCP Tools
# Note: MCPTools typically inherits the environment variables of the running process.
# Ensure ETH_RPC_URL is set in os.environ for the EVM server.

aderyn_tool = MCPTools(command="npx aderyn-mcp")
evm_tool = MCPTools(command="npx @mcpdotdirect/evm-mcp-server")
coingecko_tool = MCPTools(command="npm install coingecko-mcp", ...)

# Assign to Agents
# compliance_officer.tools.append(aderyn_tool)
# trader_agent.tools.append(evm_tool)
# market_analyst.tools.append(coingecko_tool)
```

## 5. Critical Gaps & Wrappers

The report identified gaps (Rug Pull Detection, Flashbots). These require custom wrappers.
*   **Action:** Create a new Python tool in `backend/tools/` that wraps the Sharpe.ai or Flashbots API, then expose it to Agno. There is no need to wrap it in MCP protocol specifically if it's internal; Agno native tools work just as well. MCP is best for *external* standard tools.

## 6. Conclusion
The MCP ecosystem offers powerful, ready-made capabilities. We should proceed with integrating **Aderyn**, **EVM**, and **CoinGecko** immediately. We should hold off on **Qdrant** to rely on our existing **SurrealDB** memory architecture.

## 7. References

*   **Agno MCP Documentation**: [https://docs.agno.com/basics/tools/mcp/overview](https://docs.agno.com/basics/tools/mcp/overview)
*   **Agno MCP Tools**: [https://docs.agno.com/basics/tools/mcp/tools](https://docs.agno.com/basics/tools/mcp/tools)
*   **Model Context Protocol**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
*   **MCP Servers Registry**: [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
*   **Aderyn MCP**: [https://github.com/Cyfrin/aderyn](https://github.com/Cyfrin/aderyn)
*   **EVM MCP**: [https://github.com/mcpdotdirect/evm-mcp-server](https://github.com/mcpdotdirect/evm-mcp-server)
*   **CoinGecko MCP**: [https://github.com/coingecko/coingecko-mcp](https://github.com/coingecko/coingecko-mcp)
