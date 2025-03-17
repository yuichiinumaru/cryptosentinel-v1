
// This file is now just a type definition file to maintain compatibility
// All actual agency functionality has been moved to the API service

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

// Create empty agency for backward compatibility
// New code should use the API service directly
export const agency = {
  getAgents: () => [],
  getAgent: () => undefined,
  getMessages: () => [],
  getNews: () => [],
  on: () => {},
  off: () => {},
  createMessage: () => null,
  createNewsItem: () => null,
  startSimulation: () => {}
};

export default agency;
