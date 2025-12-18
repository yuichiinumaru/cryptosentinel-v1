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
