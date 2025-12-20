# Execution Roadmap: ARTEMIS Integration

## Phase 1: The Core Ports (MVP)
*   [ ] **Task 1.1: Create BDD Scenarios for Dynamic Prompting**
    *   Adapt ARTEMIS logic to `codeswarm` context.
    *   Define "Given Context X, When Spawning Agent Y, Then Prompt Contains Z".
*   [ ] **Task 1.2: Implement `PromptBuilder` interface**
    *   **TDD:** Write failing test first (`tests/test_prompt_builder.py`).
    *   Implement the `build_prompt(template_name, context)` method.

## Phase 2: The Spawner Mechanism
*   [ ] **Task 2.1: Define `AgentRegistry` contract**
    *   Define interface compatible with our `backend/storage/` (SurrealDB/SQLite).
*   [ ] **Task 2.2: Implement Mock Spawner**
    *   Create `MockSpawner` for testing isolation without spinning up full agents.

## Phase 3: Integration
*   [ ] **Task 3.1: End-to-End test**
    *   Test flow: Supervisor -> New Worker -> Completion.

## Phase 4: Cognitive & Self-Healing (Research Integration)

### 4.1 Cognitive Infrastructure (AVI)
*   [ ] **Task 4.1.1: Create `CognitiveCoordinator` Agent**
    *   Implement state machine logic: `Retrieve` -> `Perceive` -> `Review`.
    *   Define phase-specific system prompts.
*   [ ] **Task 4.1.2: Refactor Toolkits for Phased Access**
    *   Add metadata tags to existing tools (e.g., `market_data` = `retrieve`, `quant_metrics` = `perceive`).

### 4.2 Codebase Awareness (InfCode)
*   [ ] **Task 4.2.1: Implement AST Indexer Script**
    *   Create `scripts/index_codebase.py` to parse `backend/` and build a structural map (Class/Function locations).
*   [ ] **Task 4.2.2: Develop `CodebaseToolkit`**
    *   Implement tools: `find_class_definition`, `get_function_signature`, `search_code_by_intent`.
    *   Integrate with `KhalaMemory` for semantic search over docstrings.

### 4.3 Agentic Verification (AutoRocq & DataSage)
*   [ ] **Task 4.3.1: Implement Task Tree Abstraction**
    *   Create `TaskNode` and `TaskTree` classes in `backend/orchestration/` to track goal execution state.
*   [ ] **Task 4.3.2: Implement Refinement Loop Wrapper**
    *   Create a `ToolExecutionManager` that catches specific errors (e.g., `SlippageError`) and triggers a retry with adjusted parameters.
*   [ ] **Task 4.3.3: Implement Knowledge Judge**
    *   Create a lightweight "Judge" step in `MarketAnalyst` to determine if `DuckDuckGoTools` is needed.
