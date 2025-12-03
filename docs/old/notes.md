# Notes

## Documentation

- The primary sources of truth for the project are `docs/agents.md` and `docs/agents2.md`.
- The `docs/dump.txt` file should be ignored as it contains outdated information.
- The user has provided links to the `agno` and `mem0` documentation, which should be used as a reference.

## Compatibility

- The project uses the `agno` framework for the multi-agent system.
- The project uses the `mem0` library for memory. I need to investigate how to integrate `mem0` with `agno`.
- The project uses `pydantic` for data validation and serialization.
- The project uses `fastapi` for the backend API.

## Potential Ideas and Upgrades

- **Implement full tool logic:** Many of the tools are currently placeholders. These need to be implemented with full logic.
- **Implement Knowledge Base:** Set up a vector database (e.g., ChromaDB) and implement the `ConsultKnowledgeBase` and `RAGQueryTool`.
- **Implement Backtesting Engine:** Implement the `BacktestingTool` and `OptimizeStrategyTool`.
- **Implement MCP Integration:** Implement MCP clients for non-critical tools.
- **Improve Security:** The security measures described in the documentation (e.g., Flashbots, MEV protection) need to be implemented in the `ExecuteSwap` tool.
- **Improve Error Handling:** The tools and agents need to have robust error handling.
- **Add more tests:** The tests are currently very basic. Comprehensive tests need to be added for all agents and tools.
