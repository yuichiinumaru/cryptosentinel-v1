# Implementation Plans

This document outlines the strategic plans to enhance CryptoSentinel using insights from the `TradingAgents` framework.

## Plan A: Adversarial Debate Workflow

**Objective:** Implement a "Bull vs. Bear" debate mechanism to reduce bias in trading decisions.

**Strategy:**
1.  **New Agents:** Create `BullResearcher` and `BearResearcher`. These can be standalone agents or specific persona configurations of existing analysts.
2.  **Debate Logic:** Implement a `DebateRoom` workflow (controlled by `DeepTraderManager` or a new `DebateModerator`) that cycles through:
    *   *Thesis:* Bull presents case, Bear presents case.
    *   *Rebuttal:* Bull critiques Bear, Bear critiques Bull.
    *   *Verdict:* Manager decides.
3.  **TDD Approach:**
    *   Create `tests/test_debate_workflow.py`.
    *   *Test 1:* Mock Bull and Bear agents. Verify that `DebateModerator` calls them in correct order (Bull -> Bear -> Bull -> Bear).
    *   *Test 2:* Verify that the outputs of the debate are correctly passed to the Verdict phase.
    *   *Test 3:* Verify that the final decision respects the "Winner" of the debate (logic check).

## Plan B: Situation-Aware Memory

**Objective:** Enable agents to recall similar past market situations to inform current decisions.

**Strategy:**
1.  **Memory Schema:** Define a standard JSON structure for a "Market Situation" (e.g., `{metrics: {rsi: 70, sentiment: 0.8}, outcome: "price_dropped", lessons: "..."}`).
2.  **Vector Search:** Update `KhalaMemoryToolkit` to expose `search_memory_by_vector` (mapping market metrics to vector embeddings).
3.  **Integration:**
    *   *Pre-Analysis:* `MarketAnalyst` queries memory for "Similar Market Conditions".
    *   *Post-Trade:* `LearningCoordinator` saves the "Situation" and "Outcome".
4.  **TDD Approach:**
    *   Create `tests/test_memory_integration.py`.
    *   *Test 1:* Mock `SurrealDBClient`. Verify `store_situation` correctly formats data.
    *   *Test 2:* Verify `retrieve_similar_situations` returns top-k matches based on input vector/text.

## Plan C: Deep Thinking Prompts

**Objective:** Replace brief instructions with detailed, persona-based prompts inspired by `TradingAgents`.

**Strategy:**
1.  **Audit:** Review all `instructions.md` files.
2.  **Refactor:** Rewrite them using the "Role-Task-Constraint-Output" framework.
    *   *Example:* "You are a Bullish Researcher... Your task is to find growth potential... Constraints: Use only verified data... Output format: Markdown Table."
3.  **TDD Approach:**
    *   Use `tests/test_prompts.py` (Evaluation).
    *   *Test 1:* Send a standard input to the agent with the new prompt. Verify output format (e.g., check for specific Markdown headers or JSON structure).

## Plan D: Explicit Reflection Loop

**Objective:** Mandate a learning step after every significant event.

**Strategy:**
1.  **Trigger:** Define triggers for reflection (Trade Closed, Prediction Horizon Reached).
2.  **Process:** `LearningCoordinator` wakes up, analyzes the Delta (Predicted vs. Actual), and generates a "Lesson".
3.  **Storage:** Store this lesson in `khala-agentmemory`.
4.  **TDD Approach:**
    *   Create `tests/test_reflection_loop.py`.
    *   *Test 1:* Simulate a "TradeResult" event. Verify `LearningCoordinator` is called.
    *   *Test 2:* Verify `LearningCoordinator` generates a memory entry with non-zero importance.
