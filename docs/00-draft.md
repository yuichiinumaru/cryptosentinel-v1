# Research & Discovery: ARTEMIS Architecture Harvesting

## 1. Problem Analysis
**Context:** `codeswarm` (CryptoSentinel) currently utilizes a static `AgentFactory` pattern where agents are instantiated with fixed `instructions.md` files.
**Pain Point:**
*   **Static Context:** Agents cannot easily adapt their system prompt based on real-time market conditions or specific user intent without restarting the session or complicated logic within the `instructions.md` (which is text).
*   **Rigid Topology:** The `Team` is defined at start-time (`get_crypto_trading_team`). We cannot dynamically spawn a specific "Sniper Agent" or "Deep Research Agent" on the fly in response to a Triage decision.
*   **Resource Inefficiency:** All agents in the team are instantiated even if only one is needed.

**Why ARTEMIS?**
ARTEMIS solves this with:
1.  **Dynamic Prompting:** Constructing agent personalities and constraints at runtime.
2.  **Parallel Spawning:** Launching ephemeral workers for specific tasks.
3.  **Triage:** A dedicated routing layer to optimize resource usage.

## 2. Research Findings: ARTEMIS Mechanics
*Source: ARTEMIS Framework (Rust/Python)*

### 2.1 Dynamic Prompt Generation
*   **ARTEMIS:** Uses a Rust-based template engine to assemble prompts from `Modules` (e.g., `BasePersona` + `RiskModule` + `TaskContext`).
*   **Current (`codeswarm`):** Uses static `instructions_path=".../instructions.md"`.
*   **Contrast:** ARTEMIS is composable and context-aware; `codeswarm` is static and monolithic.

### 2.2 Agent Spawning
*   **ARTEMIS:** Spawns isolated Docker containers or Rust Actors for heavy compute, controlled by a Python orchestrator.
*   **Current (`codeswarm`):** Uses `Agno`'s `Team` structure. Agents are Python objects sharing the same process/memory space (mostly).
*   **Contrast:** ARTEMIS offers high isolation and polyglot capability (Rust workers). `codeswarm` is Python-native and easier to debug but less isolated.

### 2.3 Triage
*   **ARTEMIS:** The entry point is *always* a Triage unit that classifies intent and routes to the correct spawner.
*   **Current (`codeswarm`):** The `DeepTraderManager` acts as a de-facto leader, but it's part of the mesh, not necessarily a dedicated triage gateway.

## 3. Gap Analysis

| Feature | ARTEMIS (Source) | codeswarm (Target) | Gap |
| :--- | :--- | :--- | :--- |
| **Prompting** | Modular, Runtime Assembly | Static Markdown Files | **High:** Need a `PromptBuilder`. |
| **Concurrency** | Actor Model / Docker | AsyncIO / Threading (Agno) | **Medium:** Need an `EphemeralAgent` pattern. |
| **Lifecycle** | Spawn -> Work -> Die | Session Lifecycle (Long-lived) | **High:** Need `AgentRegistry` & Lifecycle management. |
| **Routing** | Dedicated Triage Layer | Manager Agent | **Low:** Can adapt Manager to Triage. |

## 4. Assumptions & Adaptation Strategy
1.  **No Docker in Sandbox:** We cannot implement the Docker-based spawning of ARTEMIS in this environment.
2.  **Python Adaptation:** We will port the *logic* of the Rust Spawner into a Python `AgentSpawner` class that utilizes `Agno`'s factory patterns but adds lifecycle management.
3.  **Jinja2 for Prompts:** We will replace the Rust templating with Python's `Jinja2` or simple string formatting to achieve Dynamic Prompting.
