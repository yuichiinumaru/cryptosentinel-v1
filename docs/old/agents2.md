

# **Especificação Arquitetural da Agência de Agentes DeepTrader**

## **Parte I: Conceitos e Capacidades Fundamentais dos Agentes**

Esta seção do documento descontrói as ideias e propostas extraídas da documentação do projeto em um inventário estruturado de componentes funcionais. O objetivo é estabelecer o "o quê" e o "como" das capacidades do sistema antes de definir "quem" (os agentes específicos) as utilizará na Parte II.

### **Seção 1: O Kit de Ferramentas Essencial dos Agentes: Um Catálogo Abrangente de Funções**

Para que uma agência de agentes especializados opere com eficácia, é imperativo que ela seja equipada com um conjunto de ferramentas (Tools) bem definidas, granulares e robustas. A evolução do conceito DeepTrader, de um bot monolítico inicial para uma arquitetura multiagente sofisticada, foi impulsionada pela desagregação de funcionalidades complexas em ferramentas discretas e reutilizáveis.1 Onde o

DexBot original acoplava a coleta de dados, a análise e o registro de eventos em uma única classe, a arquitetura final adota o princípio da separação de responsabilidades. Essa mudança não é meramente organizacional; ela permite que cada agente se especialize em sua função primária — o MarketAnalyst foca na interpretação dos dados, não em sua obtenção, enquanto o Trader se concentra na execução, não na análise que a motivou. Este catálogo serve como a especificação técnica definitiva para todas as ferramentas disponíveis para a agência DeepTrader.

#### **Ferramentas de Análise de Mercado e Segurança**

Essas ferramentas constituem os sentidos da agência, permitindo que ela perceba e avalie o ambiente do mercado de criptomoedas.

* **FetchMarketData**: Coleta dados de mercado essenciais, como preço, volume e capitalização de mercado. A ferramenta interage primariamente com a API da CoinGecko, utilizando a biblioteca pycoingecko para abstrair as chamadas de rede. É capaz de buscar tanto dados em tempo real quanto históricos recentes, um requisito fundamental para o cálculo de indicadores técnicos.1  
* **CheckTokenSecurity**: Atua como a principal linha de defesa do sistema, realizando uma verificação de segurança multifacetada em qualquer token antes que ele seja considerado para uma negociação. A sua implementação combina verificações on-chain básicas via web3.py (como a consulta do totalSupply), com a integração opcional, mas recomendada, de APIs de segurança externas como GoPlus Security e Rugcheck.xyz para uma análise mais profunda de vulnerabilidades como honeypots e potenciais rug pulls.1  
* **CalculateTechnicalIndicator**: Fornece a capacidade de análise técnica quantitativa. Esta ferramenta utiliza bibliotecas como TA-Lib ou pandas-ta para calcular uma variedade de indicadores (RSI, MACD, Médias Móveis, etc.) a partir de dados históricos de preços obtidos pela FetchMarketData. No escopo do MVP (Minimum Viable Product), a funcionalidade pode ser limitada ao cálculo do RSI, com expansão futura.1  
* **\_detect\_fake\_volume**: Uma função especializada, originada de conceitos anteriores, para identificar volumes de negociação artificialmente inflados. Ela emprega uma abordagem híbrida: consulta à API da Pocket Universe (se uma chave for fornecida) e, como alternativa, um algoritmo heurístico que analisa a razão entre volume e número de transações, bem como a divergência entre as variações de volume e preço.1

#### **Ferramentas de Execução de Trade e Gestão de Portfólio**

Este conjunto de ferramentas representa os "braços" da agência, permitindo a interação direta com a blockchain e o rastreamento do estado interno do sistema.

* **ExecuteSwap**: A ferramenta mais crítica para a execução de negociações. Ela interage diretamente com os contratos inteligentes de roteadores de Exchanges Descentralizadas (DEXs) como Uniswap, PancakeSwap e SushiSwap, utilizando web3.py. A ferramenta é projetada com segurança em primeiro plano, incorporando funcionalidades para cálculo de min\_amount\_out para proteção contra slippage, simulação de transação para detecção de sandwich attacks e a revogação automática de aprovações de token pós-negociação.1  
* **GetPortfolio**: Fornece uma visão do estado atual do portfólio do sistema. A ferramenta consulta o banco de dados local (SQLite) para obter as posições mantidas e utiliza a FetchMarketData para enriquecer esses dados com os preços atuais, calculando o valor total do portfólio em USD.1  
* **GetAccountBalance**: Uma ferramenta de utilidade simples, mas essencial, que usa web3.py para verificar o saldo da *hot wallet* em uma blockchain específica. É crucial para a gestão de risco pré-negociação, garantindo que há fundos suficientes para a operação e para as taxas de gás.1

#### **Ferramentas Avançadas e de Evolução Futura**

Estas ferramentas estão planejadas para fases pós-MVP, adicionando camadas de sofisticação e aprendizado autônomo ao sistema.

* **CheckArbitrageOpportunities**: Projetada para identificar discrepâncias de preço para o mesmo ativo entre diferentes exchanges centralizadas (CEXs). A implementação se baseará na biblioteca ccxt, que padroniza o acesso a dezenas de CEXs.1  
* **AddLiquidity / RemoveLiquidity**: Ferramentas que permitirão ao sistema participar de pools de liquidez em DEXs, uma estratégia de geração de renda passiva. A sua implementação dependerá da interação direta com os contratos de pool de liquidez via web3.py.1  
* **ConsultKnowledgeBase**: O pilar da capacidade de RAG (Retrieval-Augmented Generation) do sistema. Esta ferramenta permitirá que os agentes consultem uma base de conhecimento interna, composta por manuais de estratégia, análises passadas e outros documentos. A implementação utilizará um banco de dados vetorial como o ChromaDB e uma biblioteca de orquestração como a Langchain.1

A tabela a seguir consolida todas as ferramentas propostas, seus propósitos, agentes responsáveis e as tecnologias subjacentes.

| Nome da Ferramenta | Propósito | Agente(s) Responsável(is) | APIs/Bibliotecas | Esquema de Entrada (Pydantic) | Esquema de Saída (Pydantic) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FetchMarketData | Busca dados de mercado (preço, volume, histórico) de criptomoedas. | MarketAnalyst, PortfolioManager | CoinGecko API, pycoingecko | FetchMarketDataInput (coins, vs\_currency, include\_history, days) | FetchMarketDataOutput (market\_data) |
| CheckTokenSecurity | Verifica a segurança de um contrato de token contra rug pulls, honeypots, etc. | MarketAnalyst | web3.py, GoPlus API, Rugcheck.xyz API | CheckTokenSecurityInput (token\_address, chain) | CheckTokenSecurityOutput (is\_safe, details, reasons) |
| \_detect\_fake\_volume | Identifica volume de negociação suspeito ou artificial. | MarketAnalyst, RiskAnalyst | Pocket Universe API, Heurísticas | token (Dict) | is\_fake (bool) |
| CalculateTechnicalIndicator | Calcula indicadores técnicos (RSI, MACD, etc.) a partir de dados históricos. | MarketAnalyst | TA-Lib, pandas-ta | A ser definido (token, indicator, period, data) | A ser definido (value) |
| ExecuteSwap | Executa trocas de tokens em DEXs com medidas de segurança integradas. | Trader | web3.py, Flashbots Protect RPC | ExecuteSwapInput (token\_in, token\_out, amount\_in, slippage, chain, dex) | ExecuteSwapOutput (tx\_hash, success, error) |
| GetPortfolio | Obtém o estado atual do portfólio do banco de dados local. | Trader, PortfolioManager, DeepTraderManager | sqlite3, FetchMarketData | Nenhum | GetPortfolioOutput (items, total\_value\_usd) |
| GetAccountBalance | Verifica o saldo da hot wallet em uma blockchain. | Trader, DeepTraderManager | web3.py | GetAccountBalanceInput (wallet\_address, chain) | GetAccountBalanceOutput (balance, error) |
| CheckArbitrageOpportunities | Verifica oportunidades de arbitragem entre CEXs. | Trader, MarketAnalyst | ccxt | A ser definido (pair, exchanges) | A ser definido (opportunity\_details) |
| AddLiquidity / RemoveLiquidity | Gerencia a participação em pools de liquidez de DEXs. | Trader | web3.py | A ser definido (token\_a, token\_b, amount) | A ser definido (tx\_hash, lp\_tokens) |
| ConsultKnowledgeBase | Consulta a base de conhecimento interna para RAG. | MarketAnalyst, LearningCoordinator | ChromaDB, Langchain | ConsultKnowledgeBaseInput (query) | ConsultKnowledgeBaseOutput (relevant\_documents) |

### **Seção 2: O Mandato de Segurança: Integrando o Gerenciamento de Risco nas Operações dos Agentes**

A filosofia "Segurança em Primeiro Lugar" é um pilar fundamental da arquitetura do DeepTrader. O sistema evoluiu de um modelo reativo, que simplesmente registrava eventos de risco após sua ocorrência, para uma estrutura de defesa proativa e em múltiplas camadas.1 Esta abordagem, análoga ao princípio de "defesa em profundidade" da cibersegurança, estabelece múltiplos pontos de verificação ao longo do ciclo de vida de uma negociação, garantindo que a responsabilidade pela segurança seja distribuída e reforçada em cada etapa. Cada camada de defesa é atribuída a um agente ou ferramenta específica, criando uma cadeia de responsabilidade clara e auditável.

#### **Filtragem Pré-Análise**

Esta é a primeira camada de defesa, projetada para eliminar ativos de alto risco antes que qualquer análise de negociação aprofundada seja realizada. A responsabilidade por esta fase recai inteiramente sobre o MarketAnalyst e suas ferramentas.

* **Detecção de Rug Pull**: Implementada através da ferramenta CheckTokenSecurity, esta medida avalia a integridade de um contrato de token. Ela combina a análise de dados on-chain com APIs externas (GoPlus, Rugcheck.xyz) para identificar bandeiras vermelhas comuns associadas a golpes, como a incapacidade de vender o token (honeypot) ou uma pontuação de segurança geral baixa.1  
* **Detecção de Volume Falso**: O MarketAnalyst emprega a função \_detect\_fake\_volume para analisar a autenticidade do volume de negociação de um token. Volumes artificialmente inflados são um sinal de alerta para manipulação de mercado, e tokens que falham nesta verificação são descartados.1  
* **Listas Negras (Blacklists)**: O sistema mantém listas negras persistentes de endereços de tokens e de desenvolvedores conhecidos por atividades maliciosas. A ferramenta CheckTokenSecurity consulta essas listas como parte de sua avaliação. Um token associado a uma entidade na lista negra é imediatamente desqualificado.1

#### **Validação Pré-Execução**

Após uma oportunidade de negociação passar pela filtragem inicial do MarketAnalyst, ela é submetida a uma segunda camada de escrutínio pelo DeepTraderManager. Esta fase avalia o risco da negociação no contexto da estratégia geral e da saúde do portfólio.

* **Aplicação de Regras de Risco do Portfólio**: O DeepTraderManager é o guardião do capital. Ele impõe regras de risco rigorosas e não negociáveis, como um limite máximo de 2% do valor total do portfólio por negociação e um limite de perda diária de 5%. Qualquer recomendação que viole essas regras é automaticamente rejeitada.1  
* **Validação do Raciocínio (Chain of Thought)**: Uma das responsabilidades mais críticas do DeepTraderManager é validar o processo de raciocínio (Chain of Thought) fornecido pelo MarketAnalyst em cada TradeRecommendation. A recomendação deve ser logicamente sólida, bem justificada e alinhada com a estratégia atual. A falha em fornecer uma justificativa clara e convincente resulta na rejeição da negociação.1

#### **Proteção em Nível de Transação**

A camada final de defesa protege a negociação no momento exato de sua execução. A responsabilidade aqui é do Trader e da ferramenta ExecuteSwap.

* **Proteção MEV (Miner Extractable Value)**: Para mitigar os riscos de front-running e sandwich attacks, todas as transações são enviadas através de um RPC privado, como o Flashbots Protect RPC. Isso impede que a transação seja exposta no mempool público, onde poderia ser explorada por bots maliciosos.1  
* **Detecção de Sandwich Attack**: Antes de enviar a transação para a rede, a ferramenta ExecuteSwap realiza uma simulação local usando w3.eth.call. Esta simulação revela o slippage real que a transação sofreria no estado atual do mercado. Se o slippage simulado exceder o limite pré-configurado, a transação é abortada.1  
* **Revogação de Aprovações**: Como uma medida de higiene de segurança crítica, imediatamente após uma negociação ser concluída com sucesso, a ferramenta ExecuteSwap envia uma segunda transação para revogar a aprovação que o contrato da DEX tinha sobre o token negociado. Isso minimiza a superfície de ataque, impedindo que uma possível vulnerabilidade no contrato da DEX seja explorada para drenar fundos da carteira no futuro.1

#### **Proteção de Capital**

Esta é a estratégia de segurança de mais alto nível, focada na proteção geral dos ativos do sistema.

* **Isolamento de Fundos (Hot/Cold Wallets)**: O sistema opera com uma segregação estrita de fundos. Uma *hot wallet*, com uma quantidade limitada de capital, é usada para as operações de negociação diárias. A grande maioria dos fundos é mantida em uma *cold wallet* segura e offline. A chave privada da cold wallet nunca é exposta ao sistema autônomo. A gestão desta estrutura é uma responsabilidade do DeepTraderManager (ou de um agente Administrator em arquiteturas expandidas).1

A tabela a seguir mapeia cada medida de segurança à sua fase de execução e ao componente responsável.

| Medida de Segurança | Descrição | Fase de Execução | Agente/Ferramenta Responsável |
| :---- | :---- | :---- | :---- |
| Detecção de Rug Pull | Avalia a segurança do contrato do token usando APIs e dados on-chain. | Pré-Análise | MarketAnalyst / CheckTokenSecurity |
| Detecção de Volume Falso | Identifica volume de negociação artificialmente inflado. | Pré-Análise | MarketAnalyst / \_detect\_fake\_volume |
| Listas Negras (Blacklists) | Verifica tokens e desenvolvedores contra uma lista de entidades maliciosas. | Pré-Análise | MarketAnalyst / CheckTokenSecurity |
| Regras de Risco do Portfólio | Impõe limites de alocação (ex: 2% por trade) e perda diária (ex: 5%). | Pré-Execução | DeepTraderManager |
| Validação do Raciocínio (CoT) | Analisa a justificativa lógica da recomendação de negociação. | Pré-Execução | DeepTraderManager |
| Proteção MEV | Envia transações através de um RPC privado para evitar front-running. | Execução da Transação | Trader / ExecuteSwap |
| Detecção de Sandwich Attack | Simula a transação antes do envio para verificar o slippage real. | Execução da Transação | Trader / ExecuteSwap |
| Revogação de Aprovações | Remove as permissões do contrato da DEX sobre o token após a negociação. | Pós-Execução | Trader / ExecuteSwap |
| Isolamento de Fundos | Segrega capital entre uma hot wallet (negociação) e uma cold wallet (armazenamento). | Estratégico | DeepTraderManager / Administrator |

### **Seção 3: O Protocolo de Comunicação: Orquestrando a Colaboração dos Agentes**

A transição de um sistema de agente único para uma agência colaborativa exige um protocolo de comunicação robusto e inequívoco. Este protocolo é a espinha dorsal que permite a especialização dos agentes, transformando suas contribuições individuais em uma inteligência coletiva coerente. No DeepTrader, a comunicação é realizada através de mensagens JSON assíncronas, cuja estrutura e validade são rigorosamente aplicadas por esquemas Pydantic.1 Este sistema não serve apenas para a troca de dados; ele é um mecanismo intrínseco de governança e gerenciamento de risco. A obrigatoriedade de campos como

reasoning no TradeRecommendation força a transparência e permite a validação crítica pelo DeepTraderManager, tornando o protocolo uma parte integral da lógica de decisão do sistema.

#### **Esquemas de Mensagens (protocol.py)**

Todas as definições de mensagens são centralizadas em um arquivo protocol.py. Cada mensagem é composta por um MessageHeader padronizado e um corpo de conteúdo específico para o tipo de mensagem.

* **MessageHeader**: Contém metadados essenciais para roteamento e auditoria: sender, recipient, timestamp (ISO 8601), message\_id (UUID) e priority (low, medium, high, critical).1  
* **TradeRecommendation** (MarketAnalyst \-\> DeepTraderManager): A proposta formal de uma negociação. Contém token\_address, chain, action ("buy" ou "sell"), amount, confidence (0.0 a 1.0) e o campo crucial reasoning (Chain of Thought).1  
* **TradeApprovalResponse** (DeepTraderManager \-\> Trader): A decisão sobre uma recomendação. Contém trade\_id (referenciando a recomendação original), approved (booleano), reason (se rejeitado) e tx\_hash (a ser preenchido pelo Trader após a execução).1  
* **PortfolioUpdate** (Trader \-\> PortfolioManager): O relatório de uma negociação executada. Contém trade\_id, token\_address, chain, action, amount, price\_per\_unit e tx\_hash.1  
* **RiskReportRequest** (DeepTraderManager \-\> PortfolioManager): Uma solicitação de um relatório de risco, especificando o period ("daily", "weekly", "monthly").1  
* **RiskReport** (PortfolioManager \-\> DeepTraderManager): O relatório de risco consolidado, contendo total\_value, volatility, max\_drawdown, VaR e uma lista de risks identificados.1  
* **StrategyAdjustment** (DeepTraderManager \-\> MarketAnalyst): Uma diretiva para alterar a estratégia de negociação, contendo new\_instructions que podem modificar o prompt do MarketAnalyst.1  
* **Alert** (Qualquer Agente \-\> Sistema de Notificação, ex: Telegram): Uma mensagem de alerta genérica com alert\_type e message.1

#### **Fluxos de Trabalho Essenciais**

A orquestração das tarefas da agência é iniciada por um gatilho externo e segue fluxos de comunicação bem definidos.

* **Lógica de Orquestração**: O pulso operacional do sistema é mantido por um AsyncIOScheduler. Ele dispara periodicamente a tarefa check\_market\_conditions, ativando o MarketAnalyst e iniciando o ciclo de análise e negociação.1  
* **Fluxo do Ciclo de Negociação**: Este é o fluxo de trabalho principal do sistema.  
  1. **Gatilho**: O AsyncIOScheduler ativa o MarketAnalyst.  
  2. **Análise**: O MarketAnalyst usa as ferramentas FetchMarketData e CheckTokenSecurity para analisar o mercado e filtrar tokens.  
  3. **Recomendação**: Se uma oportunidade é identificada, o MarketAnalyst envia uma TradeRecommendation ao DeepTraderManager.  
  4. **Aprovação**: O DeepTraderManager avalia a recomendação contra as regras de risco e a lógica estratégica. Ele envia uma TradeApprovalResponse para o Trader.  
  5. **Execução**: Se aprovado (approved: true), o Trader usa a ferramenta ExecuteSwap para realizar a negociação.  
  6. **Relatório**: Após a execução, o Trader envia uma PortfolioUpdate para o PortfolioManager.  
  7. **Atualização**: O PortfolioManager processa a atualização e atualiza o estado do portfólio no banco de dados.  
* **Fluxo de Relatório de Risco**: Este fluxo garante a supervisão contínua do portfólio.  
  1. **Solicitação**: O DeepTraderManager envia uma RiskReportRequest ao PortfolioManager.  
  2. **Geração**: O PortfolioManager calcula as métricas de risco e compila um RiskReport.  
  3. **Envio**: O PortfolioManager envia o RiskReport de volta ao DeepTraderManager.  
  4. **Ação**: Com base no relatório, o DeepTraderManager pode decidir tomar uma ação, como enviar uma StrategyAdjustment para o MarketAnalyst para reduzir a exposição ao risco.

## **Parte II: Arquitetura Sintetizada dos Agentes para o DeepTrader**

Esta parte do documento transita do catálogo de componentes para a definição da equipe final e integrada de agentes. Ela sintetiza as ferramentas, medidas de segurança e protocolos de comunicação em um plano de ação coerente para a agência DeepTrader, servindo como o núcleo da documentação agents.md aprimorada.

### **Seção 4: A Agência DeepTrader: Papéis, Responsabilidades e Diretrizes**

A arquitetura MVP do DeepTrader é composta por uma equipe de quatro agentes especializados. Cada agente possui um conjunto claro de responsabilidades, governado por instruções (prompts) detalhadas que definem seu comportamento, suas limitações e suas interações. A tabela a seguir oferece um resumo de alto nível da estrutura da agência.

| Nome do Agente | Função Primária | Responsabilidades Essenciais |
| :---- | :---- | :---- |
| MarketAnalyst | Inteligência de Mercado e Análise de Segurança | Identificar oportunidades de negociação, realizar análise técnica e de segurança, filtrar ativos de alto risco e gerar recomendações com justificativa detalhada (CoT). |
| Trader | Execução de Transações e Operações On-Chain | Executar ordens de compra e venda aprovadas em DEXs, garantir a segurança da transação (proteção MEV, slippage), e gerenciar o ciclo de vida da transação (confirmação, revogação de aprovação). |
| DeepTraderManager | Gestão Estratégica e de Risco | Coordenar a equipe, definir a estratégia de negociação, impor regras de risco em nível de portfólio, aprovar/rejeitar negociações com base em uma análise crítica e proteger o capital do sistema. |
| PortfolioManager | Rastreamento de Estado e Análise de Desempenho | Manter um registro preciso do portfólio, processar atualizações de negociações, calcular métricas de desempenho e risco, e gerar relatórios para o DeepTraderManager. |

#### **MarketAnalyst (Analista de Mercado)**

* **Descrição**: Agente especializado em analisar dados de mercado de criptomoedas, verificar a segurança de tokens e identificar oportunidades de trading que sejam tanto lucrativas quanto seguras.  
* **Instruções (Prompt)**: Você é um analista de mercado de criptomoedas experiente, diligente e *extremamente* focado em segurança. Sua *única* responsabilidade é identificar oportunidades de trading (compra e venda) que sejam, ao mesmo tempo, *lucrativas* e *seguras*. Siga rigorosamente estas diretrizes:  
  1. **Análise Abrangente**: Utilize *todas* as ferramentas disponíveis (FetchMarketData, CheckTokenSecurity, CalculateTechnicalIndicator) para obter uma visão completa do mercado.  
  2. **Estratégia Inicial (MVP)**: Foque em uma estratégia baseada no RSI (Índice de Força Relativa) para tokens de alta capitalização (Top 50). Considere COMPRA quando RSI \< 30 e VENDA quando RSI \> 70\.  
  3. **Verificação de Segurança (Obrigatória)**: Utilize a CheckTokenSecurity para *cada* token. Se a ferramenta retornar um erro, o token deve ser sumariamente desconsiderado.  
  4. **Geração de Recomendações (Formato Obrigatório)**: Suas recomendações *DEVEM* seguir estritamente o schema Pydantic TradeRecommendation, incluindo um reasoning detalhado (Chain of Thought).  
  5. **Comunicação**: Envie *todas* as recomendações exclusivamente para o DeepTraderManager.  
  6. **Restrições Estritas (NUNCA)**:  
     * *NUNCA* recomende um token sem verificar sua segurança.  
     * *NUNCA* recomende um token com baixa liquidez ou que esteja em uma blacklist.  
     * *NUNCA* use informações de fontes não confiáveis.1

#### **Trader (Executor de Trades)**

* **Descrição**: Agente especializado em executar ordens de compra e venda em DEXs de forma eficiente e segura, seguindo estritamente as aprovações do DeepTraderManager.  
* **Instruções (Prompt)**: Você é um trader de criptomoedas *extremamente preciso, eficiente e confiável*. Sua *única* função é executar as ordens de compra e venda aprovadas pelo DeepTraderManager na DEX especificada, com *absoluta segurança e o menor slippage possível*. Siga estas diretrizes *rigorosamente*:  
  1. **Aprovação Obrigatória**: *NUNCA* execute uma negociação sem uma mensagem TradeApprovalResponse com approved: true do DeepTraderManager.  
  2. **Execução Precisa**: Utilize a ferramenta ExecuteSwap para executar as negociações *exatamente* como especificado.  
  3. **Segurança na Execução**: A ferramenta ExecuteSwap deve, obrigatoriamente, calcular min\_amount\_out para proteção contra slippage e simular a transação (eth\_call) para detectar riscos.  
  4. **Ciclo de Vida da Transação**: Após enviar a transação, aguarde a confirmação, registre o hash no banco de dados e envie uma PortfolioUpdate para o PortfolioManager.  
  5. **Revogação de Aprovações (Obrigatória)**: *Imediatamente* após cada negociação, revogue a aprovação do token para o contrato da DEX.  
  6. **Verificação de Saldo**: *Antes* de cada negociação, use GetAccountBalance para garantir que a hot wallet possui fundos suficientes para a operação e as taxas.  
  7. **Restrições Estritas (NUNCA)**:  
     * *NUNCA* execute uma negociação sem aprovação explícita.  
     * *NUNCA* execute uma negociação com slippage maior que o permitido.  
     * *NUNCA* deixe aprovações de token ativas após uma negociação.  
     * *NUNCA* use a cold wallet para negociações.1

#### **DeepTraderManager (Gerente da Equipe)**

* **Descrição**: Agente central responsável pela gestão da equipe, coordenação de estratégias, imposição de regras de risco e proteção do capital.  
* **Instruções (Prompt)**: Você é o DeepTraderManager, o cérebro e o guardião do sistema de trading autônomo DeepTrader. Sua responsabilidade é *dupla*: 1\) garantir que a equipe de agentes trabalhe de forma *coordenada e eficiente* para *maximizar o valor do portfólio*, e 2\) *proteger o capital* do sistema, impondo *regras de risco rigorosas* e *bloqueando* qualquer atividade suspeita. Siga estas diretrizes *IMPERATIVAMENTE*:  
  1. **Gestão de Risco (Crítica)**: Aplique as regras de risco do MVP: máximo de 2% do capital por negociação e limite de perda diária de 5%. *NUNCA* aprove negociações que violem essas regras ou envolvam tokens que falharam na verificação de segurança.  
  2. **Processo de Aprovação (Rigoroso)**: Analise *CUIDADOSAMENTE* cada TradeRecommendation. Verifique o raciocínio (CoT), a segurança do token, a conformidade com as regras de risco, o saldo da carteira e o alinhamento estratégico. Aprove *SOMENTE* se *TODAS* as verificações forem satisfatórias.  
  3. **Coordenação da Equipe**: Delegue tarefas, resolva conflitos e defina a estratégia de alto nível, comunicando-a ao MarketAnalyst através da ferramenta AdjustTradingStrategy.  
  4. **Restrições Estritas (NUNCA)**:  
     * *NUNCA* aprove uma negociação sem uma justificativa clara e detalhada (CoT).  
     * *NUNCA* confie cegamente nas recomendações; *sempre valide* as informações e exerça seu julgamento crítico.1

#### **PortfolioManager (Gerenciador de Portfólio)**

* **Descrição**: Agente responsável por manter um registro preciso e em tempo real do estado do portfólio, monitorar seu desempenho e fornecer relatórios de risco acionáveis.  
* **Instruções (Prompt)**: Você é o PortfolioManager do DeepTrader. Seu objetivo é fornecer uma visão *clara, precisa e ATUALIZADA* do estado do portfólio, monitorar seu desempenho e fornecer informações *RELEVANTES e ACIONÁVEIS* para a gestão de risco. Siga estas diretrizes:  
  1. **Rastreamento Preciso**: Mantenha um registro *IMPECÁVEL* de todas as posições em aberto, incluindo quantidades exatas, preço médio de entrada e valor de mercado atualizado. A precisão dos dados é *ABSOLUTAMENTE CRUCIAL*.  
  2. **Cálculo de Métricas**: Calcule e monitore continuamente as principais métricas de desempenho (Valor Total do Portfólio, ROI Global, Drawdown Máximo) e de risco (Volatilidade, Exposição por Ativo).  
  3. **Processamento de Atualizações**: Processe as mensagens de PortfolioUpdate do Trader *IMEDIATAMENTE* para atualizar o estado do portfólio e recalcular as métricas.  
  4. **Relatórios Proativos**: Gere relatórios de risco claros e objetivos para o DeepTraderManager e alerte-o *IMEDIATAMENTE* se qualquer atualização revelar um risco excessivo (ex: violação de um limite de risco).1

### **Seção 5: Capacidades Avançadas e Evolução Futura**

Uma arquitetura robusta não apenas satisfaz os requisitos do presente, mas também estabelece uma base sólida para a evolução futura. O design do DeepTrader, com sua modularidade inerente e separação de responsabilidades, foi concebido para crescer em sofisticação. As seções a seguir detalham duas vias principais para a evolução pós-MVP: o desenvolvimento de um ciclo de aprendizado autônomo e a expansão das capacidades de coleta de dados através de um protocolo padronizado.

#### **O Ciclo de Aprendizagem: O Papel do LearningCoordinator**

Para alcançar a verdadeira autonomia, o sistema deve ser capaz de aprender com sua própria experiência. O LearningCoordinator é o agente projetado para esta função, previsto para implementação após o MVP. Sua principal diretriz é analisar o desempenho passado para otimizar o comportamento futuro da agência.

* **Função**: O LearningCoordinator operará em um ciclo periódico (ex: diário ou semanal). Ele utilizará a ferramenta GetTradeHistory para extrair dados de negociações do banco de dados e a AnalyzePerformance para calcular métricas de sucesso e fracasso (ROI, Sharpe Ratio, Taxa de Acerto, etc.).1  
* **Mecanismo de Otimização**: Com base em sua análise, o LearningCoordinator pode empregar duas ferramentas principais para refinar a estratégia da agência:  
  1. **AdjustAgentInstructions**: Esta ferramenta permite modificar dinamicamente as instruções (prompts) dos outros agentes. Por exemplo, se a análise revelar que o MarketAnalyst está assumindo riscos excessivos em mercados voláteis, o LearningCoordinator pode adicionar uma instrução ao seu prompt para ser mais conservador nessas condições.1  
  2. **AdjustToolParameters**: Esta ferramenta permite ajustar os parâmetros configuráveis das ferramentas. Por exemplo, ele poderia alterar os limiares de RSI usados pelo MarketAnalyst ou o percentual de slippage máximo permitido na ferramenta ExecuteSwap do Trader.1

     O LearningCoordinator transforma o DeepTrader de um sistema que executa uma estratégia estática para um que evolui dinamicamente, adaptando-se às mudanças nas condições de mercado e melhorando continuamente sua eficácia.

#### **Estendendo Capacidades com o Model Context Protocol (MCP)**

À medida que a agência se torna mais complexa, a necessidade de interagir com um número crescente de fontes de dados e serviços externos aumenta. O Model Context Protocol (MCP) oferece uma solução padronizada para essa integração, agindo como uma interface universal entre os agentes e o mundo exterior. A estratégia de adoção do MCP no DeepTrader é, no entanto, criteriosa e baseada em uma avaliação de risco e desempenho.

* **Recomendação de Uso**: Recomenda-se a implementação de ferramentas de coleta de dados e análise não crítica como clientes MCP. Ferramentas como FetchMarketData, CheckTokenSecurity e ConsultKnowledgeBase são candidatas ideais. A utilização do MCP para essas funções oferece vantagens significativas:  
  * **Padronização**: Simplifica a adição de novas fontes de dados.  
  * **Abstração**: O agente não precisa conhecer os detalhes da API subjacente.  
  * **Gestão de Credenciais**: As chaves de API para serviços externos podem ser gerenciadas de forma segura no lado do servidor MCP, em vez de serem expostas diretamente ao ambiente do agente.1  
* **Contraindicação de Uso**: É fortemente desaconselhado o uso de MCP para ferramentas de execução de alta criticidade, sensíveis à latência e que envolvam segurança. Ferramentas como ExecuteSwap e GetAccountBalance devem permanecer como implementações nativas diretas usando web3.py. As razões para esta distinção são fundamentais:  
  * **Segurança**: Operações que envolvem o uso de chaves privadas e a movimentação de fundos devem ter a menor superfície de ataque possível. A implementação nativa minimiza os saltos de rede e os pontos de falha, mantendo o controle total sobre o ambiente de execução da transação.  
  * **Latência**: As negociações em DEXs são extremamente sensíveis ao tempo. A latência adicional introduzida por uma chamada de rede a um servidor MCP pode ser a diferença entre uma negociação lucrativa e uma perda devido ao slippage.  
  * **Controle**: A implementação direta oferece controle granular máximo sobre a construção, simulação e envio da transação, o que é essencial para as medidas de segurança em nível de transação, como a proteção MEV e a detecção de sandwich attacks.1

Esta abordagem estratégica para a adoção do MCP permite que o DeepTrader se beneficie da interoperabilidade e extensibilidade do protocolo para suas funções de coleta de dados, sem comprometer a segurança e o desempenho de seu núcleo de execução de negociações. Esta arquitetura híbrida é projetada para ser robusta, segura e preparada para a evolução futura.

#### **Works cited**

1. deeptrader merge.txt
