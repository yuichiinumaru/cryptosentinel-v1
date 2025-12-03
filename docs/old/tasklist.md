# Tasklist

## Phase 1: Scaffolding and Core Agents

- [x] **Create Project Structure**
    - [x] Create directories for all 12 agents.
    - [x] Create `instructions.md`, `files/`, and `schemas/` for each agent.
    - [x] Create a central `/tools` directory.
    - [x] Create `protocol.py` for communication schemas.
- [x] **Implement Storage Layer**
    - [x] Define `Storage` abstract base class.
    - [x] Define data models in `models.py`.
    - [x] Implement `SqliteStorage`.
- [x] **Implement `MarketAnalyst` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement `FetchMarketData` tool.
    - [x] Implement `CheckTokenSecurity` tool.
    - [x] Implement `CalculateTechnicalIndicator` tool.
    - [x] Implement `MarketAnalyst` agent.
- [x] **Implement `Trader` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement wallet management tools (`GetAccountBalance`, `GetGasPrice`, `GetTransactionReceipt`).
    - [x] Implement DEX tools (`ExecuteSwap`, `ExecuteTransactionSimulation`, `RevokeApprovalTool`) (placeholders).
    - [x] Implement CEX tools (`ExecuteOrder`, `GetOrderBook`) (placeholders).
    - [x] Implement `Trader` agent.
- [x] **Implement `DeepTraderManager` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement portfolio tools (`GetPortfolio`).
    - [x] Implement communication tools (`ApproveTradeTool`, `RejectTradeTool`).
    - [x] Implement risk management tools (`AdjustGlobalRiskParameters`, `PauseTradingTool`).
    - [x] Implement `DeepTraderManager` agent.
- [x] **Implement `PortfolioManager` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement portfolio analysis tools (`CalculatePortfolioMetrics`, `CalculatePortfolioRisk`, `GetTradeHistoryFromDB`).
    - [x] Implement `PortfolioManager` agent.
- [x] **Implement `AnalistaFundamentalista` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement fundamental analysis tools (`FetchNewsTool`, `FetchFundamentalDataTool`, `AnalyzeDocumentTool`, `FetchBlockchainDataTool`, `FetchSocialMediaTool`).
    - [x] Implement `AnalistaFundamentalista` agent.
- [x] **Implement `AnalistaDeSentimento` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement sentiment analysis tools (`AnalyzeSentimentTool`, `SendInternalAlertTool`).
    - [x] Implement `AnalistaDeSentimento` agent.
- [x] **Implement `RiskAnalyst` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement risk analysis tools (`CalculateRiskMetricsTool`, `ManageBlacklistTool`, `DetectAnomaliesTool`, `StressTestingTool`).
    - [x] Implement `RiskAnalyst` agent.
- [x] **Implement `StrategyAgent` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement strategy analysis tools (`AnalyzePerformanceTool`, `FetchHistoricalDataTool`, `CheckArbitrageOpportunitiesTool`, `IdentifyMarketRegimeTool`).
    - [x] Implement `StrategyAgent` agent.
- [x] **Implement `AssetManager` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement asset management tools (`MonitorTransactionsTool`, `CheckWalletSecurityTool`, `SystemMonitoringTool`, `SecureTransferTool`, `FetchSecretTool`).
    - [x] Implement `AssetManager` agent.
- [x] **Implement `ComplianceOfficer` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement compliance tools (`ComplianceCheckTool`, `CalculateFeesTool`, `GenerateFinancialReportsTool`, `RegulatoryWatchTool`).
    - [x] Implement `ComplianceOfficer` agent.
- [x] **Implement `LearningCoordinator` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement learning tools (`KnowledgeStorageTool`, `AnalyzeAgentPerformanceTool`, `AdjustAgentInstructionsTool`, `AdjustToolParametersTool`).
    - [x] Implement `LearningCoordinator` agent.
- [x] **Implement `Dev` Agent**
    - [x] Write `instructions.md`.
    - [x] Implement dev tools (`DevelopmentEnvironmentTool`, `VersionControlTool`, `ContainerizationTool`, `CICDTool`, `DependencyManagementTool`, `TestingFrameworkTool`, `ProjectManagementTool`, `DocumentationGeneratorTool`).
    - [x] Implement `Dev` agent.

## Phase 2: Integration and Testing

- [ ] **Integrate Agents**
    - [ ] Update `Agency` instance in `main.py` to include all agents.
    - [ ] Implement the communication flow between agents using the defined protocol.
- [ ] **Write Comprehensive Tests**
    - [ ] Write unit tests for all tools.
    - [ ] Write integration tests for the agents.
    - [ ] Write end-to-end tests for the multi-agent system.

## Phase 3: Advanced Features

- [ ] **Implement Full Tool Logic**
    - [ ] Replace placeholder implementations with full logic for all tools.
- [ ] **Implement Knowledge Base**
    - [ ] Set up a vector database (e.g., ChromaDB).
    - [ ] Implement `ConsultKnowledgeBase` and `RAGQueryTool`.
- [ ] **Implement Backtesting Engine**
    - [ ] Implement `BacktestingTool` and `OptimizeStrategyTool`.
- [ ] **Implement MCP Integration**
    - [ ] Implement MCP clients for non-critical tools.
