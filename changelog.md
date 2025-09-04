# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-09-04

### Added
- **Gemini Model Integration**: Reconfigured the entire agent backend to use Google's Gemini model instead of OpenAI.
- **API Key Rotation**: Implemented a `KeyManager` to rotate through a list of API keys, enhancing resilience to resource exhaustion errors.
- **In-Memory Database**: Added a simple in-memory storage solution (`storage.py`) to persist trades and agent activities during a session.
- **Custom Agent Tools**: Created custom tools (`record_trade_tool`, `record_activity_tool`) for agents to interact with the in-memory database.
- **Live API Endpoints**: Implemented the `/trades/recent`, `/agent/activities/recent`, and `/market/price` endpoints with live, agent-driven data.
- **Project Documentation**: Created `tasklist.md` for tracking progress and `deployment_guide.md` for setup instructions.
- **Robust Streaming**: Improved the `/chat` endpoint's streaming logic to handle complex event objects from the agent framework.

### Changed
- **Consolidated Backend Logic**: Refactored `key_manager.py` and `storage.py` into `agents.py` to resolve persistent module loading and circular dependency issues.
- **Updated `package.json`**: Modified npm scripts to use `npx` for better compatibility.

### Fixed
- **Module Not Found Errors**: Resolved numerous `ModuleNotFoundError` issues by creating the `backend/__init__.py` file and correcting import paths to be absolute.
- **Server Startup Failures**: Debugged and fixed multiple server startup failures related to incorrect dependencies and module pathing.
- **Frontend Build Process**: Repaired the frontend build process by performing a clean `npm install` and fixing script commands.

## [Unreleased] - 2025-09-04

### Added
- Created initial Python backend using FastAPI.
- Implemented API endpoints with mock data as specified in `README.md`.
- Defined a multi-agent team (MarketAnalyst, Trader, LearningManager, Manager) using the Agno framework.
- Integrated the agent team into the API for the `/news/latest` and `/chat` endpoints.

### Changed
- Refactored backend authentication to be compliant with the frontend's expected `Authorization: Bearer <key>` header.
- Configured the Vite frontend server to use IPv4 to resolve a network error in the execution environment.

### Fixed
- Resolved multiple Python dependency issues (`ddgs`, `openai`).
- Corrected several `Agno` framework usage errors related to class names and constructor arguments for `Agent` and `Team`.
