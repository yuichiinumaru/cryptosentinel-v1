
// Agency Swarm Multi-Agent Framework
// This is a simplified version for demonstration purposes

import { toast } from "@/components/ui/use-toast";

// Define Agent types
export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  tools: string[];
  instructions: string;
  isActive: boolean;
}

// Define Message types
export type MessageRole = "system" | "user" | "assistant" | "function";

export interface Message {
  id: string;
  agentId: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

// Define News Item type
export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  url?: string;
  timestamp: Date;
  sentiment: "positive" | "negative" | "neutral";
  relevance: number; // 0-100
  tags: string[];
  coins?: string[];
  agentId: string; // Which agent discovered/analyzed this news
}

// Define the Agency (handles multi-agent coordination)
class Agency {
  private agents: Agent[] = [];
  private messages: Message[] = [];
  private news: NewsItem[] = [];
  private listeners: Map<string, Function[]> = new Map();
  
  constructor() {
    this.initializeAgents();
  }
  
  private initializeAgents() {
    // Create the four agents you specified
    this.agents = [
      {
        id: "market-analyst",
        name: "MarketAnalyst",
        role: "Market Intelligence",
        description: "Analyzes market data, verifies token security, recommends trades, and monitors malicious activity",
        tools: [
          "searchNews", 
          "consultKnowledgeBase", 
          "fetchMarketData", 
          "checkTokenSecurity",
          "getTokenPrice",
          "calculateTechnicalIndicators",
          "analyzeSentiment",
          "getPricePrediction"
        ],
        instructions: "Monitor crypto markets, analyze tokens, identify trends, and share important news.",
        isActive: true
      },
      {
        id: "trader",
        name: "Trader",
        role: "Trading Execution",
        description: "Executes buy and sell orders, manages the portfolio",
        tools: [
          "executeSwap", 
          "getPortfolio", 
          "getAccountBalance", 
          "checkArbitrageOpportunities",
          "executeArbitrageTrade"
        ],
        instructions: "Execute trades efficiently based on strategies and market conditions.",
        isActive: true
      },
      {
        id: "learning-manager",
        name: "LearningManager",
        role: "System Optimization",
        description: "Analyzes system performance and adjusts agent strategies for continuous learning",
        tools: [
          "getTradeHistory", 
          "analyzePerformance", 
          "adjustAgentInstructions", 
          "adjustToolParameters"
        ],
        instructions: "Improve system performance through continuous analysis and learning.",
        isActive: true
      },
      {
        id: "manager",
        name: "Manager",
        role: "Team Coordination",
        description: "Manages the team, sets goals, monitors performance, and manages risks",
        tools: [
          "getAllAgentTools", 
          "monitorRisk", 
          "optimizeCapitalAllocation", 
          "manageBlacklist"
        ],
        instructions: "Coordinate agent activities, manage risks, and ensure system goals are met.",
        isActive: true
      }
    ];
  }
  
  // Simulate message creation between agents
  public createMessage(agentId: string, content: string, role: MessageRole = "assistant"): Message {
    const message: Message = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      agentId,
      role,
      content,
      timestamp: new Date()
    };
    
    this.messages.push(message);
    this.emit("message", message);
    return message;
  }
  
  // Simulate news item creation
  public createNewsItem(
    title: string, 
    summary: string, 
    source: string, 
    sentiment: "positive" | "negative" | "neutral" = "neutral",
    agentId: string = "market-analyst",
    tags: string[] = [],
    coins: string[] = []
  ): NewsItem {
    const newsItem: NewsItem = {
      id: `news-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      title,
      summary,
      source,
      timestamp: new Date(),
      sentiment,
      relevance: Math.floor(Math.random() * 100),
      tags,
      coins,
      agentId
    };
    
    this.news.push(newsItem);
    this.emit("news", newsItem);
    
    // Show toast for important news
    if (newsItem.relevance > 75) {
      toast({
        title: "Important News",
        description: newsItem.title,
        variant: "default"
      });
    }
    
    return newsItem;
  }
  
  // Get all agents
  public getAgents(): Agent[] {
    return [...this.agents];
  }
  
  // Get agent by ID
  public getAgent(id: string): Agent | undefined {
    return this.agents.find(agent => agent.id === id);
  }
  
  // Get all messages
  public getMessages(limit: number = 50): Message[] {
    return [...this.messages].slice(-limit);
  }
  
  // Get all news
  public getNews(limit: number = 50): NewsItem[] {
    return [...this.news].slice(-limit).sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }
  
  // Event system
  public on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }
  
  public off(event: string, callback: Function) {
    if (!this.listeners.has(event)) return;
    
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      this.listeners.set(
        event, 
        callbacks.filter(cb => cb !== callback)
      );
    }
  }
  
  private emit(event: string, data: any) {
    if (!this.listeners.has(event)) return;
    
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error("Error in event callback:", error);
        }
      });
    }
  }
  
  // Start simulation to generate sample data
  public startSimulation() {
    // Generate sample news every 10-20 seconds
    setInterval(() => {
      if (Math.random() > 0.5) {
        this.simulateNewsDiscovery();
      }
    }, 10000 + Math.random() * 10000);
    
    // Generate agent communications every 5-15 seconds
    setInterval(() => {
      if (Math.random() > 0.6) {
        this.simulateAgentCommunication();
      }
    }, 5000 + Math.random() * 10000);
  }
  
  private simulateNewsDiscovery() {
    const topics = [
      { title: "Bitcoin breaks $70,000 resistance", sentiment: "positive" as const, tags: ["BTC", "price", "breakout"], coins: ["BTC"] },
      { title: "Ethereum 2.0 upgrade launches successfully", sentiment: "positive" as const, tags: ["ETH", "upgrade", "staking"], coins: ["ETH"] },
      { title: "SEC approves spot Ethereum ETF", sentiment: "positive" as const, tags: ["ETH", "regulation", "ETF"], coins: ["ETH"] },
      { title: "Regulatory crackdown on crypto exchanges", sentiment: "negative" as const, tags: ["regulation", "exchanges"], coins: [] },
      { title: "New vulnerability found in smart contract protocol", sentiment: "negative" as const, tags: ["security", "smart-contracts"], coins: [] },
      { title: "Major bank launches crypto custody service", sentiment: "positive" as const, tags: ["adoption", "institutional"], coins: [] },
      { title: "Cardano announces partnership with African nation", sentiment: "positive" as const, tags: ["ADA", "adoption", "partnership"], coins: ["ADA"] },
      { title: "DeFi protocol hacked, $10M lost", sentiment: "negative" as const, tags: ["DeFi", "security", "hack"], coins: [] },
      { title: "Solana network experiences downtime", sentiment: "negative" as const, tags: ["SOL", "network", "outage"], coins: ["SOL"] },
      { title: "NFT market shows signs of recovery", sentiment: "positive" as const, tags: ["NFT", "market"], coins: [] }
    ];
    
    const sources = ["CoinDesk", "CoinTelegraph", "The Block", "Bloomberg", "Decrypt", "Forbes", "Reuters"];
    const topic = topics[Math.floor(Math.random() * topics.length)];
    const source = sources[Math.floor(Math.random() * sources.length)];
    
    this.createNewsItem(
      topic.title,
      `Analysis from MarketAnalyst: ${topic.title}. This could have significant implications for the ${topic.tags.join(", ")} sectors.`,
      source,
      topic.sentiment,
      "market-analyst",
      topic.tags,
      topic.coins
    );
  }
  
  private simulateAgentCommunication() {
    const communications = [
      { from: "market-analyst", to: "trader", content: "BTC showing a bullish divergence on the 4h chart. Consider preparing for entry." },
      { from: "trader", to: "manager", content: "Executed BTC long position at $68,245. Stop loss set at $66,500." },
      { from: "learning-manager", to: "market-analyst", content: "Your ETH analysis last week resulted in +12% ROI. Updating your strategy parameters." },
      { from: "manager", to: "trader", content: "Risk exposure to altcoins is high. Consider reducing positions in small caps." },
      { from: "market-analyst", to: "manager", content: "Detected potential scam activity in token 0x8F23...A412. Adding to blacklist." },
      { from: "trader", to: "learning-manager", content: "Trading volume is unusually low today. Adjusting position sizes accordingly." },
      { from: "learning-manager", to: "manager", content: "System performance +8.2% this week. Strategy optimization complete." },
      { from: "manager", to: "market-analyst", content: "Focus on blue chip DeFi tokens this week. Requesting detailed analysis." }
    ];
    
    const comm = communications[Math.floor(Math.random() * communications.length)];
    this.createMessage(comm.from, comm.content);
    setTimeout(() => {
      this.createMessage(comm.to, `Response to ${this.getAgent(comm.from)?.name}: Acknowledged. Processing your information.`);
    }, 2000 + Math.random() * 3000);
  }
}

// Create and export a singleton instance
export const agency = new Agency();

// Start simulation for development/demo purposes
agency.startSimulation();

export default agency;
