# Forge Rules: ARTEMIS Patterns

## 1. Dynamic Prompting
*   **Rule:** **All Prompting Must Be Stateless.**
    *   *Why:* Prompts are rebuilt on every spawn. Do not rely on hardcoded strings in Python files. Use the `PromptBuilder` and templates.
    *   *Constraint:* Templates must be stored in `backend/prompts/templates/`.

## 2. Agent Lifecycle
*   **Rule:** **Workers Must Be Ephemeral.**
    *   *Why:* To prevent context bloat and resource leaks.
    *   *Pattern:* Spawn -> Execute Task -> Report -> Terminate. Do not keep Worker agents alive across unrelated requests.
*   **Rule:** **Triage Must Be Independent.**
    *   *Why:* The Triage agent must not hold complex domain knowledge. Its only job is routing.

## 3. State Management
*   **Rule:** **No Shared Mutable State.**
    *   *Why:* Even in a single process, treat agents as if they are on separate machines (Actor Model). Use the Database or passed `Context` objects to share data, never global variables.
