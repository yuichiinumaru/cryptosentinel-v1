# Arquitetura de Agentes (DeepTrader agno - Implementação Completa)

**Filosofia do Projeto:** O DeepTrader é uma equipe de agentes autônomos baseada em LLM, operando dentro do framework agno. A LLM tem controle total sobre as ferramentas de análise, a carteira e a interação com exchanges (DEX/CEX), tomando decisões de compra/venda e movimentando fundos de forma independente, seguindo a estratégia definida e os parâmetros de risco. Não há regras de trading "hardcoded"; a LLM "pensa" e decide qual ação tomar com base no contexto, ferramentas e objetivos, visando exclusivamente maximizar o valor da carteira dentro dos limites de risco estabelecidos. O desenvolvimento segue uma filosofia **RBI (Research, Backtest, Implement)**. O sistema é projetado para operar de forma contínua e autônoma, **com logging detalhado e tratamento robusto de erros em todas as operações.**
**Arquitetura Geral:** O sistema utiliza uma arquitetura multiagente com comunicação assíncrona. Agentes especializados colaboram, utilizando ferramentas (`Tools`) customizadas. RAG é usado para contexto adicional via **File Search** (habilitado por padrão em todos os agentes) e ferramentas dedicadas (`ConsultKnowledgeBase`, `RAGQueryTool`). A persistência de dados é crucial para aprendizado e auditoria. A segurança é prioritária em todas as operações.
**Nota sobre Estrutura e Ferramentas:** Cada agente terá sua própria pasta dedicada (ex: `/MarketAnalyst`, `/Trader`), contendo seu arquivo de definição Python (`MarketAnalyst.py`), seu arquivo de instruções (`instructions.md`), e subpastas para arquivos específicos (`files/`, `schemas/`). No entanto, todas as ferramentas Python customizadas (`BaseTool`) residirão em um diretório central compartilhado `/tools`. Os agentes referenciarão e carregarão as ferramentas necessárias a partir deste diretório central em suas definições, promovendo reutilização e manutenção centralizada do código das ferramentas.
**Persistência e Aprendizado:** A base de dados (inicialmente SQLite, com plano de migração para PostgreSQL/MongoDB, utilizando schemas definidos via SQLAlchemy) armazenará não apenas o histórico de trades e o estado do portfólio, mas também:
*   **Decisões e Raciocínios:** Logs detalhados das recomendações do `MarketAnalyst` (incluindo scores de segurança), aprovações/rejeições do `DeepTraderManager`, e o *Chain of Thought* (CoT) associado a cada decisão significativa.
*   **Resultados de Ferramentas:** Saídas de ferramentas críticas (ex: `CheckTokenSecurity` scores e detalhes, indicadores calculados, resultados de simulação pré-trade) para análise posterior pelo `LearningCoordinator` e auditoria.
*   **Feedback e Métricas:** Dados de desempenho de trades individuais e gerais, métricas de portfólio (ROI, Drawdown, Volatilidade, Sharpe), e, futuramente, feedback explícito gerado pelo `LearningCoordinator` para ajuste de instruções.
*   **Base de Conhecimento RAG:** Vetores e metadados para documentos de pesquisa, análises passadas, insights de mercado, e documentação interna (gerenciados via ChromaDB/Langchain, como explorado em `docs/chromadb.md` e `docs/Vectordb_with_chroma.ipynb`). Serão exploradas técnicas avançadas de RAG (HyDE, Re-ranking, Self-RAG) pelo `LearningCoordinator`.
*   **Blacklists:** Listas de tokens e desenvolvedores (se identificáveis) considerados de alto risco, gerenciadas pelo `RiskAnalyst` via `ManageBlacklistTool`.
*   **Dados Transitórios:** O mecanismo `shared_state` do agno (acessível via `self._shared_state` nas ferramentas) pode ser utilizado por ferramentas para passar dados temporários entre chamadas sequenciais dentro da mesma execução de um agente (ex: contexto RAG recuperado por uma ferramenta para ser usado pela próxima), mas não substitui a persistência no banco de dados ou o logging detalhado.
**Segurança (Detalhes Adicionais):**
*   **API Keys & Wallet Keys:** Gerenciamento seguro via variáveis de ambiente (`.env`) ou, preferencialmente, via Secret Manager (HashiCorp Vault, AWS/Google Secret Manager). Chaves de API e de wallet são tratadas como identidades seguras e clientes async (`async-hvac`, `aiobotocore`) buscados em runtime pelas ferramentas (`FetchSecretTool`). Auditoria e rotação de chaves serão implementadas. (Referência: `research/agents-research.md`)
*   **Proteção MEV:** Uso mandatório de RPCs privados como Flashbots Protect RPC (configurado via `.env`) ao interagir com DEXs via `web3.py`. (Referência: `old/deeptrader dump.txt`)
*   **Proteção Sandwich/Slippage:** Uso mandatório de simulação pré-trade (`eth_call` ou `ExecuteTransactionSimulationTool`) antes de qualquer execução de swap em DEX para prever resultados, detectar slippage inesperado e potenciais ataques sandwich. (Referência: `old/deeptrader dump.txt`, `old/deeptrader project v2.txt`)
*   **Revogação de Aprovações (DEX):** Automatizada e imediata após cada trade usando `RevokeApprovalTool` ou lógica integrada na ferramenta `ExecuteSwap`. (Referência: `old/deeptrader dump.txt`, `old/deeptrader project v2.txt`)
*   **Isolamento de Fundos:** Utilização de hot wallets (para trading ativo, gerenciadas pelo `Gestor de Ativos` e usadas pelo `Trader`) e cold wallets (hardware wallets para armazenamento seguro de longo prazo). Transferências entre elas são controladas e monitoradas. (Referência: `old/deeptrader dump.txt`, `old/deeptrader project.txt`)
*   **Monitoramento de Contratos:** `CheckTokenSecurity` inclui verificações contra honeypots, taxas anormais, e consulta a blacklists. Alertas sobre interações com contratos desconhecidos ou maliciosos pelo `Gestor de Ativos`.
*   **Rate Limiting e Circuit Breakers:** Implementados nas interações com APIs externas e nas lógicas internas das ferramentas para prevenir abuso ou falhas em cascata.
*   **Kill Switch:** Implementação de um mecanismo de "kill switch" manual e automático (ativado por `DeepTraderManager` ou `RiskAnalyst` baseado em regras de drawdown máximo) para pausar todas as operações de trading em emergências. (Referência: `old/deeptrader swarm.txt`)
**Foco:** A implementação visa abranger todos os agentes e funcionalidades descritas, construindo um sistema de trading autônomo completo e robusto desde o início. A filosofia de agno foi escolhida por sua adequação a sistemas multiagentes, ferramentas customizáveis e autonomia de LLM. (Referência: `old/deeptrader swarm.txt`)
**Loop Principal e Agendamento:** O sistema opera continuamente (24/7) usando uma combinação de `agency.run_loop()` (agno para processamento de mensagens e execução de tarefas iniciadas pelos agentes) e `AsyncIOScheduler` (APScheduler) para tarefas periódicas como análise de mercado pelo `MarketAnalyst` (atuando como scanner), verificação de risco pelo `RiskAnalyst`, e atualização de dados pelo `PortfolioManager`. (Referência: `old/deeptrader swarm.txt`)
**Comunicação:** A comunicação entre agentes é assíncrona e baseada em mensagens JSON padronizadas, validadas por schemas Pydantic definidos em `protocol.py`. **O framework agno gerencia essa comunicação através da ferramenta `SendMessage`, que utiliza a descrição (`description`) de cada agente para determinar o destinatário correto, de acordo com as permissões definidas no `agency_chart`. Por isso, descrições claras, únicas e distintas são essenciais para o roteamento confiável.** Cada mensagem contém um `header` (remetente, destinatário, timestamp, ID da mensagem, prioridade opcional) e um `body` (tipo de mensagem, conteúdo específico, contexto relevante). O arquivo `protocol.py` define a estrutura exata para cada tipo de interação, incluindo (mas não limitado a): `TradeRecommendation`, `TradeApprovalRequest`, `TradeApprovalResponse`, `PortfolioUpdate`, `RiskReportRequest`, `RiskReport`, `StrategyAdjustment`, `LearningUpdate`, e `Alert`. Técnicas de robustez como retentativas (`tenacity`) e potencialmente Dead Letter Queues (DLQ) podem ser implementadas para garantir a entrega e o processamento de mensagens críticas. (Referência: `old/deeptrader swarm.txt`, `old/deeptrader project v2.txt`)
**Agentes da Equipe DeepTrader:**
*   **MarketAnalyst**
*   **Trader** (Antigo Broker)
*   **PortfolioManager**
*   **DeepTraderManager** (Antigo Diretor de Trading)
*   **AnalistaFundamentalista**
*   **AnalistaDeSentimento**
*   **RiskAnalyst**
*   **StrategyAgent**
*   **AssetManager** (Gestor de Ativos - Segurança e Custódia)
*   **ComplianceOfficer** (Oficial de Conformidade)
*   **LearningCoordinator**
*   **Dev** (Meta-Agente)

---

**Descrição Detalhada dos Agentes e Ferramentas (Implementação Completa)**

**Configuração Padrão dos Agentes:**

Salvo indicação contrária, todos os agentes serão inicializados com os seguintes parâmetros base. Parâmetros específicos como `api_key`, `base_url` (para endpoints customizados como Ollama ou APIs Google compatíveis) e o nome exato do `model` serão carregados a partir de variáveis de ambiente (`.env`). O uso de Pydantic V2 (`>=2.0.0`) é recomendado. (Referência: `old/deeptrader project v2.txt`, `old/deeptrader2.txt`). **Durante o desenvolvimento, considere usar `response_validator` para verificações de qualidade de saída e `examples` para guiar comportamentos complexos.**

*   `name`: (Definido para cada agente) - **Essencial para identificação e menção (@).**
*   `description`: (Definido para cada agente) - **CRÍTICO para roteamento de mensagens via `SendMessage`. Deve ser claro, único e descritivo da função.**
*   `model`: (Definido via `.env` - e.g., `gemini-1.5-flash`, `gemini-1.5-pro`, ou modelo Ollama via endpoint compatível)
*   `temperature`: 0.7
*   `top_p`: 1.0
*   `max_prompt_tokens`: `None` (Utiliza o default do modelo)
*   `max_completion_tokens`: `None` (Utiliza o default do modelo)
*   `parallel_tool_calls`: `True` (Exceto onde especificado)
*   `truncation_strategy`: `{"type": "auto"}`
*   `instructions`: Carregado de `./instructions.md` (relativo à pasta do agente)
*   `tools`: Lista de ferramentas carregadas do diretório `/tools`.
*   `tools_folder`: `None` (Ferramentas são carregadas explicitamente da pasta `/tools` central)
*   `files_folder`: `./files` (Relativo à pasta do agente)
*   `schemas_folder`: `./schemas` (Relativo à pasta do agente, para ferramentas baseadas em OpenAPI, se aplicável)
*   `file_search`: `True` (**Habilitado por padrão para todos**, permitindo acesso a arquivos em `files_folder` e `shared_files` da agência, se houver)
*   `code_interpreter`: `False` (**Desabilitado por padrão**. Habilitar explicitamente para agentes que precisam, como `Dev`, `StrategyAgent` ou `LearningCoordinator`).
*   `response_validator`: `None` (Pode ser definido como um método da classe do Agente para validação customizada)
*   `examples`: `[]` (Lista de exemplos de conversas user/assistant para few-shot prompting)

**1. MarketAnalyst (Analista de Mercado Técnico)**

*   **Responsável por:** Atuar como um **scanner de mercado contínuo**, analisando dados de múltiplos tokens (pré-definidos ou dinamicamente selecionados), aplicando indicadores técnicos (`TA-Lib`, `Pandas TA`), identificando padrões gráficos, verificando rigorosamente a segurança dos tokens (`CheckTokenSecurity`) e gerando recomendações de trading de curto prazo seguras e justificadas para o `DeepTraderManager`. (Nota: instalação do TA-Lib pode requerer atenção especial. Referência: `old/deeptrader project v2.txt`).
*   **Descrição (para roteamento):** "Analista Técnico Quantitativo e de Segurança de Tokens. Opera como scanner contínuo, identificando oportunidades de trading (curto prazo) usando análise técnica (RSI, SMA, MACD, padrões). Verifica MANDATORIAMENTE a segurança de tokens (honeypots, taxas, liquidez, GoPlus/Rugcheck, blacklist) antes de qualquer recomendação. Justifica com CoT."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `FetchMarketData` (busca dados de preço/volume para múltiplos tokens de DEX/CEX)
    *   `CheckTokenSecurity` (usa APIs externas e verificações on-chain, consulta `ManageBlacklistTool`)
    *   `CalculateTechnicalIndicator` (utiliza `TA-Lib`, `Pandas TA`)
    *   `ConsultKnowledgeBase` (para pesquisas internas, análises passadas)
    *   `IdentifyChartPatternsTool`
    *   `BacktestingTool` (para validações rápidas de sinais em um token específico)
    *   `VisualizeDataTool` (para gráficos de indicadores/padrões)
    *   `ManageBlacklistTool` (Consulta a blacklist mantida pelo `RiskAnalyst`)
    *   `RAGQueryTool`

**2. AnalistaFundamentalista (Analista Fundamentalista)**

*   **Responsável por:** Avaliar o valor intrínseco das criptomoedas, monitorar notícias de fontes confiáveis, analisar whitepapers, roadmaps, equipes, tokenomics e dados on-chain relevantes, fornecendo insights para decisões de investimento de médio/longo prazo e contexto para o `DeepTraderManager`.
*   **Descrição (para roteamento):** "Analista Fundamentalista Cripto. Avalia valor intrínseco (tokenomics, equipe, tecnologia, roadmap, whitepapers, notícias, dados on-chain - holders, txs). Fornece relatórios de avaliação fundamentalista e monitora eventos chave (lançamentos, parcerias)."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
    *   Pode precisar de `max_completion_tokens` maior para gerar relatórios detalhados.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `FetchNewsTool` (com fontes configuráveis e filtro de relevância)
    *   `FetchFundamentalDataTool` (CoinGecko API, dados on-chain básicos)
    *   `AnalyzeDocumentTool` (para whitepapers, relatórios)
    *   `FetchBlockchainDataTool` (Etherscan API, etc.)
    *   `FetchSocialMediaTool` (para canais oficiais de projetos)
    *   `ConsultKnowledgeBase` (para dados históricos, regulamentos)
    *   `RAGQueryTool`

**3. AnalistaDeSentimento (Analista de Sentimento do Mercado)**

*   **Responsável por:** Coletar, analisar e quantificar o sentimento do mercado em tempo real a partir de diversas fontes online (redes sociais como X/Twitter, Reddit, notícias, fóruns), identificando tendências, FUD/FOMO e emitindo alertas.
*   **Descrição (para roteamento):** "Analista de Sentimento do Mercado Cripto. Monitora e quantifica sentimento em tempo real (redes sociais, notícias). Calcula índices de sentimento (VADER, NLP), identifica tendências FUD/FOMO e emite alertas sobre mudanças abruptas."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `FetchSocialMediaTool` (APIs de X, Reddit, etc.)
    *   `FetchNewsTool`
    *   `AnalyzeSentimentTool` (VADER, spaCy, ou modelos mais avançados)
    *   `VisualizeDataTool` (gráficos de sentimento ao longo do tempo)
    *   `SendInternalAlertTool` (para `DeepTraderManager`, `RiskAnalyst`)
    *   `ConsultKnowledgeBase`

**4. RiskAnalyst (Analista de Risco)**

*   **Responsável por:** Identificar, avaliar, monitorar e mitigar riscos (mercado: VaR, volatilidade; crédito: contraparte CEX; operacional: falhas de sistema/API; segurança: hacks, exploits; viés de sobrevivência em dados). Gerencia a blacklist de tokens/devs, detecta anomalias (volume falso, etc.) e **define/monitora políticas quantificáveis de SL/TP (ex: Stop Loss 2%, Take Profit 5% por trade) e tamanho máximo de posição (ex: 1% do capital por trade)** em colaboração com `StrategyAgent` e `DeepTraderManager`.
*   **Descrição (para roteamento):** "Analista de Risco Quantitativo e de Segurança. Monitora risco de portfólio (VaR, volatilidade, drawdown) e ativos (segurança via CheckTokenSecurity, anomalias). Gerencia blacklist. Define e monitora políticas de risco (SL/TP % por trade, max size %, max drawdown %) com Estrategista e Manager. Alerta sobre violações e riscos elevados."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `CalculateRiskMetricsTool` (VaR, Sharpe, Sortino, Max Drawdown)
    *   `CheckTokenSecurity` (Utiliza dados desta ferramenta)
    *   `ManageBlacklistTool` (Adiciona/Remove/Consulta tokens/devs)
    *   `DetectAnomaliesTool` (Volume/Tx Ratio, Volume/Price Divergence - ref: `old/deeptrade1.txt`. Pode usar Pocket Universe API ou heurísticas.)
    *   `SendInternalAlertTool`
    *   `ExecuteTransactionSimulationTool` (para avaliar riscos de execução antes de aprovação)
    *   `StressTestingTool` (simula cenários de mercado adversos no portfólio)
    *   `ConsultKnowledgeBase`
    *   `GetPortfolio` (para dados atuais)

**5. StrategyAgent (Agente de Estratégia)**

*   **Responsável por:** Sintetizar análises de todos os analistas (Técnico, Fundamental, Sentimento, Risco), desenvolver, testar rigorosamente (backtesting), otimizar e propor estratégias de trading completas (regras de entrada/saída, dimensionamento de posição, SL/TP) adaptadas a diferentes regimes de mercado identificados. **Considera tanto estratégias complexas quanto estratégias quantitativas simples e bem definidas (ex: cruzamento de EMAs como 9-EMA).** Considera oportunidades de arbitragem CEX/DEX.
*   **Descrição (para roteamento):** "Desenvolvedor de Estratégias Quantitativas. Cria, testa (backtesting rigoroso com BacktestingTool) e otimiza estratégias (incluindo simples como EMA Crossover) com base em análises combinadas (técnica, fundamental, sentimento, risco). Define regras (entrada/saída, SL/TP), adapta a regimes de mercado. Avalia arbitragem."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`.
    *   **`code_interpreter=True`** (Potencialmente útil para análises de backtest, manipulação de dados, ou otimizações).
    *   Pode necessitar de `max_completion_tokens` maior para descrever estratégias complexas.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `BacktestingTool` (Usa `backtrader` ou similar, integra dados históricos e simula execução)
    *   `AnalyzePerformanceTool` (Analisa resultados do backtest)
    *   `FetchHistoricalDataTool` (Para múltiplos ativos e timeframes)
    *   `OptimizeStrategyTool` (Otimização de parâmetros usando `optuna` ou similar)
    *   `CheckArbitrageOpportunitiesTool` (Usa `ccxt` para comparar preços CEX/DEX)
    *   `IdentifyMarketRegimeTool` (Classifica o estado atual do mercado - volátil, tendência, range)
    *   `CalculateTechnicalIndicator`
    *   `ConsultKnowledgeBase`
    *   `RAGQueryTool`
    *   `VisualizeDataTool`

**6. Trader (Executor de Trades)**

*   **Responsável por:** Executar ordens de compra/venda (após aprovação explícita do `DeepTraderManager`) nas DEXs (via `web3.py`) e CEXs (via `ccxt`) de forma precisa, eficiente, segura, com mínimo slippage e aplicando todas as medidas de segurança pré e pós-trade (simulação, revogação de aprovação).
*   **Descrição (para roteamento):** "Executor de Trades Cripto (DEX/CEX). Executa ordens APROVADAS com precisão e segurança. Gerencia slippage (DEX), realiza simulação pré-trade OBRIGATÓRIA (DEX), confirma txs, e executa revogação OBRIGATÓRIA de aprovações (DEX)."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
    *   `parallel_tool_calls`: **`False`** - **Garante a sequência crítica: Simular -> Executar -> Revogar (se DEX).**
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `ExecuteSwap` (Interage com Router DEX via `web3.py`, inclui cálculo de `min_amount_out`, uso de RPC seguro como Flashbots)
    *   `ExecuteOrder` (Interage com APIs CEX via `ccxt` para ordens limit/market)
    *   `GetAccountBalance` (Verifica saldo antes/depois do trade)
    *   `GetTransactionReceipt` (Confirma execução e obtém detalhes)
    *   `RevokeApprovalTool` (Revoga aprovação do token específico para o Router DEX imediatamente após `ExecuteSwap`)
    *   `ExecuteTransactionSimulationTool` (**Chamada obrigatória antes de `ExecuteSwap`**)
    *   `GetOrderBook` (Para CEX, verificar liquidez antes de `ExecuteOrder`)
    *   `GetGasPrice` (Para otimizar tx em DEX)
    *   `FetchMarketData` (Verificação de preço último segundo antes da execução, se necessário)

**7. PortfolioManager (Gestor de Portfólio)**

*   **Responsável por:** Rastrear precisamente todas as posições e saldos do portfólio em tempo real (DEX wallets, CEX accounts), calcular métricas de desempenho (ROI, P&L realizado/não realizado) e risco (volatilidade, exposição), e gerar relatórios claros e precisos para o `DeepTraderManager` e `LearningCoordinator`. Atua como a fonte da verdade para o estado atual do portfólio. **O rastreamento robusto via banco de dados é crucial para superar a gestão de estado mais simples de bots básicos.**
*   **Descrição (para roteamento):** "Gestor e Analista de Portfólio Cripto. Rastreia posições e saldos em tempo real (DEX/CEX via BD). Calcula e reporta métricas de desempenho (ROI, P&L, Drawdown, Sharpe) e risco (Volatilidade, VaR, Exposição). Guardião da precisão dos dados do portfólio."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `GetPortfolio` (Agrega dados de wallets e CEXs via BD, calcula valor atualizado usando `FetchMarketData`)
    *   `FetchMarketData` (Para obter preços atuais dos ativos)
    *   `CalculatePortfolioMetrics` (Calcula P&L, ROI, Sharpe, etc.)
    *   `CalculatePortfolioRisk` (Calcula Volatilidade, VaR, exposição)
    *   `VisualizePortfolioTool` (Gera gráficos de alocação, desempenho)
    *   `PortfolioOptimizationTool` (Para análises what-if ou recomendações de rebalanceamento baseadas em modelos - Markowitz, etc.)
    *   `GetAccountBalance` (Ferramenta primária para obter saldos de wallets/CEXs)
    *   `GetTradeHistoryFromDB` (Acessa DB para calcular P&L realizado)

**8. AssetManager (Gestor de Ativos - Segurança e Custódia)**

*   **Responsável por:** Garantir a segurança máxima, custódia adequada (configuração e monitoramento de hot/cold wallets) e integridade operacional dos ativos digitais. Gerencia o fluxo seguro de fundos entre wallets e exchanges, monitora transações suspeitas e realiza auditorias de segurança periódicas. Implementa e monitora `WalletManager` (lógica interna ou classe dedicada).
*   **Descrição (para roteamento):** "Gestor de Segurança de Ativos Cripto e Custódia. Garante segurança de wallets (hot/cold, monitoramento) e chaves (via Secret Manager). Monitora transações suspeitas, realiza auditorias, gerencia fluxo seguro de fundos. Implementa políticas de WalletManager."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `MonitorTransactionsTool` (Monitora wallets controladas via Etherscan API ou similar)
    *   `CheckWalletSecurityTool` (Verifica permissões, contratos aprovados)
    *   `HardwareWalletIntegrationTool` (Para operações de transferência de/para cold wallet que exijam interação semi-manual segura)
    *   `SystemMonitoringTool` (Verifica logs de acesso, integridade do sistema)
    *   `SecureTransferTool` (Executa transferências entre wallets/exchanges controladas com checagens de segurança)
    *   `GetAccountBalance` (Para auditoria e reconciliação)
    *   `FetchSecretTool` (Interface segura para obter chaves/APIs do Secret Manager)

**9. ComplianceOfficer (Oficial de Conformidade)**

*   **Responsável por:** Assegurar conformidade com leis, regulamentações (quando aplicáveis ao trading de cripto) e políticas internas definidas. Gerenciar relatórios financeiros (para contabilidade interna) e cálculo de taxas de transação.
*   **Descrição (para roteamento):** "Oficial de Conformidade e Finanças Cripto. Garante conformidade com políticas internas e regulamentações. Gerencia auditorias internas, cálculo de taxas e prepara dados para relatórios financeiros/fiscais."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `ComplianceCheckTool` (Verifica trades contra políticas internas)
    *   `CalculateFeesTool` (Calcula taxas de gas e de exchange por trade/período)
    *   `GenerateFinancialReportsTool` (Gera sumários de P&L, taxas para contabilidade)
    *   `ProjectManagementTool` (Para rastrear tarefas de conformidade)
    *   `RegulatoryWatchTool` (Monitora notícias sobre regulamentação cripto relevante)
    *   `ConsultKnowledgeBase` (Para políticas internas, regulamentos)
    *   `GetTradeHistoryFromDB`

**10. LearningCoordinator (Coordenador de Aprendizagem)**

*   **Responsável por:** Orquestrar o ciclo de aprendizado e melhoria contínua da agência. Analisa desempenho passado (trades, decisões de agentes, logs de CoT), identifica padrões de sucesso/falha, propõe ajustes em instruções/estratégias/parâmetros de ferramentas (filosofia RBI), gerencia a base de conhecimento RAG e combate vieses cognitivos. Implementa a estratégia de auto-aprendizado.
*   **Descrição (para roteamento):** "Coordenador de Aprendizagem e Otimização Cripto. Analisa desempenho histórico (trades, CoT). Identifica padrões, propõe melhorias (estratégias/instruções/ferramentas - RBI). Gerencia base de conhecimento RAG. Implementa ciclo de feedback para auto-aprendizado."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`.
    *   **`code_interpreter=True`** (Provavelmente útil para análise de dados de desempenho).
    *   Pode necessitar de `max_completion_tokens` maior para análises e propostas detalhadas.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `GetTradeHistoryFromDB` (Acessa DB para dados de trades, incluindo CoT associado)
    *   `KnowledgeStorageTool` (Interface para adicionar/atualizar/gerenciar a base de conhecimento RAG - ChromaDB)
    *   `AnalyzeAgentPerformanceTool` (Analisa logs, CoT, métricas de decisão dos agentes)
    *   `RAGQueryTool` (Consulta a base de conhecimento vetorial)
    *   `OptimizeModelsTool` (Potencialmente usa ML para refinar modelos internos de previsão ou análise de risco - futuro)
    *   `BacktestingTool` (Para testes A/B de propostas de ajuste)
    *   `GetPortfolio` (Para dados históricos de desempenho)
    *   `AdjustAgentInstructionsTool` (Capacidade de propor modificações nas instruções de outros agentes para o Dev/Manager revisar/aplicar)
    *   `AdjustToolParametersTool` (Capacidade de propor ajustes nos parâmetros de ferramentas)

**11. Dev (Meta-Agente)**

*   **Responsável por:** Ciclo de vida completo do desenvolvimento de software das ferramentas compartilhadas em `/tools`, do `protocol.py`, da infraestrutura de execução e integrações. **Inclui a implementação de padrões robustos de logging detalhado e tratamento de erros (ex: retentativas com `tenacity`) dentro das ferramentas.** Segue processo iterativo (RBI aplicado ao desenvolvimento), responde a solicitações de novas ferramentas ou ajustes do `LearningCoordinator` ou `DeepTraderManager`.
*   **Descrição (para roteamento):** "Desenvolvedor de Ferramentas e Infraestrutura (DevOps). Cria, testa, mantém ferramentas Python em /tools e protocol.py. Implementa logging e error handling robustos nas ferramentas. Gerencia CI/CD, monitoramento, ambiente (Docker). NÃO executa trades nem acessa chaves de produção."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`.
    *   **`code_interpreter=True`** (Essencial para tarefas de desenvolvimento e testes).
    *   **Não** deve ter acesso a ferramentas de execução de trade (`ExecuteSwap`, `ExecuteOrder`), gestão de ativos sensíveis (`SecureTransferTool`, `HardwareWalletIntegrationTool`) ou chaves de produção (`FetchSecretTool` com acesso a segredos de produção).
*   **Ferramentas (Referência - Carregadas de `/tools` - Foco em Dev Tools):**
    *   `DevelopmentEnvironmentTool` (Representa o ambiente local/dev)
    *   `VersionControlTool` (Git/GitHub via comandos ou API)
    *   `ContainerizationTool` (Docker via comandos)
    *   `CICDTool` (Interação com GitHub Actions API, se necessário)
    *   `SystemMonitoringTool` (Consulta APIs de Prometheus/Grafana/Datadog)
    *   `DependencyManagementTool` (Poetry/PDM via comandos)
    *   `TestingFrameworkTool` (`pytest` via comandos)
    *   `ProjectManagementTool` (Interação com API Taiga/Jira)
    *   `DocumentationGeneratorTool` (`mkdocs`/`Sphinx` via comandos)
    *   `ConsultKnowledgeBase` (para documentação técnica, APIs de terceiros)

**12. DeepTraderManager (Gerente da Equipe e Estrategista Chefe)**

*   **Responsável por:** Liderança estratégica da agência, coordenação da comunicação e fluxo de trabalho entre agentes, gestão de risco final (aprovação/rejeição de trades com base em análises e **parâmetros de risco globais como SL/TP %, Max Position Size %**), definição de metas de alto nível, garantia de alinhamento com a estratégia geral, segurança operacional e lucratividade. Atua como o ponto central de decisão e controle.
*   **Descrição (para roteamento):** "Gerente Geral Cripto, Estrategista Chefe e Controlador de Risco Final (CEO/CIO). Lidera equipe, coordena agentes via `agency_chart`. Define metas e estratégia. Aprova/Rejeita recomendações (MarketAnalyst, StrategyAgent) com base em risco (incluindo SL/TP %, max size %) e estratégia. Guardião do capital e ativação Kill Switch."
*   **Configuração Específica:**
    *   Utiliza a configuração padrão. `file_search=True`. `code_interpreter=False`.
    *   Pode necessitar de `max_completion_tokens` maior para comunicações estratégicas e justificativas de decisão.
*   **Ferramentas (Referência - Carregadas de `/tools`):**
    *   `GetPortfolio` (Visão geral do estado atual)
    *   `GetAccountBalance` (Visão geral dos saldos)
    *   `ApproveTradeTool` (Envia mensagem de aprovação para o `Trader`)
    *   `RejectTradeTool` (Envia mensagem de rejeição com justificativa)
    *   `CommunicationHubTool` (Monitoramento de mensagens importantes - parte do framework/logging)
    *   `GetAgentReports` (Solicita/recebe relatórios sumários dos analistas e `PortfolioManager`)
    *   `AdjustGlobalRiskParameters` (Define limites de drawdown, exposição máxima por ativo/trade, SL/TP padrão %)
    *   `PauseTradingTool` (Ativa/desativa o Kill Switch global)
    *   `ConsultKnowledgeBase` (para relatórios consolidados, estratégias passadas, logs de decisão)
    *   `RAGQueryTool`

---
**Observações Gerais (Implementação Completa):**

*   **Implementação Completa:** Todos os 12 agentes e suas funcionalidades descritas são parte do escopo inicial.
*   **Segurança:** Prioridade máxima em todas as fases. Flashbots, simulação pré-trade, `CheckTokenSecurity`, revogação de aprovações, gestão segura de ativos via Secret Manager, e Kill Switch são mandatórios.
*   **Exchanges:** Operação em DEXs (via `web3.py`) e CEXs (via `ccxt`) conforme definido pelas estratégias.
*   **LLM:** Configuração centralizada via `.env`, permitindo flexibilidade (Google, Anthropic, Ollama compatível). GPT-4o ou modelos Claude 3 Opus são boas opções iniciais.
*   **Parâmetros:** Conjunto padrão de parâmetros para consistência, carregados via `.env` sempre que possível.
*   **Banco de Dados:** SQLite para desenvolvimento/testes iniciais, migração planejada para PostgreSQL/MongoDB para produção/escalabilidade. Esquema definido com SQLAlchemy.
*   **Testes:** Rigorosos em testnet (Sepolia, BSC Testnet, etc.), simulações (`BacktestingTool`) e potencialmente paper trading antes de deployment com capital real.
*   **Código:** Manter alta qualidade: modularidade (agentes em pastas, ferramentas em `/tools`), documentação clara (Docstrings, `mkdocs`), testes unitários/integração (`pytest`), linting/formatação, e seguir melhores práticas Python (async/await, tipagem estática).
