
import { toast } from "@/components/ui/use-toast";

// Base API URL - replace with your actual API URL
// This can be stored in localStorage or configured in the settings
const DEFAULT_API_URL = "http://localhost:8000"; // Default fallback

/**
 * Get the configured API URL from localStorage or use default
 */
export const getApiUrl = (): string => {
  return localStorage.getItem("apiUrl") || DEFAULT_API_URL;
};

/**
 * Set the API URL in localStorage
 */
export const setApiUrl = (url: string): void => {
  localStorage.setItem("apiUrl", url);
};

/**
 * Get the API key from localStorage
 */
export const getApiKey = (): string | null => {
  return localStorage.getItem("openaiApiKey");
};

/**
 * Basic fetch wrapper with error handling
 */
const fetchWithAuth = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const apiUrl = getApiUrl();
  const apiKey = getApiKey();
  
  const url = `${apiUrl}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  
  const headers = {
    "Content-Type": "application/json",
    ...(apiKey && { "Authorization": `Bearer ${apiKey}` }),
    ...options.headers,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    toast({
      title: "API Request Failed",
      description: error instanceof Error ? error.message : "Unknown error occurred",
      variant: "destructive",
    });
    throw error;
  }
};

// API endpoints for different data types
export const api = {
  // News endpoints
  news: {
    getAll: () => fetchWithAuth("/news"),
    getLatest: (limit = 20) => fetchWithAuth(`/news/latest?limit=${limit}`),
    getByTag: (tag: string) => fetchWithAuth(`/news/tags/${tag}`),
    getBySentiment: (sentiment: string) => fetchWithAuth(`/news/sentiment/${sentiment}`),
  },
  
  // Trade endpoints
  trades: {
    getAll: () => fetchWithAuth("/trades"),
    getRecent: (limit = 10) => fetchWithAuth(`/trades/recent?limit=${limit}`),
    execute: (tradeData: any) => fetchWithAuth("/trades/execute", {
      method: "POST",
      body: JSON.stringify(tradeData),
    }),
  },
  
  // Agent activity endpoints
  agentActivity: {
    getAll: () => fetchWithAuth("/agent/activities"),
    getByType: (type: string) => fetchWithAuth(`/agent/activities/type/${type}`),
    getRecent: (limit = 20) => fetchWithAuth(`/agent/activities/recent?limit=${limit}`),
  },
  
  // AI Learning system endpoints
  learning: {
    getLearnings: () => fetchWithAuth("/ai/learnings"),
    getDatabase: () => fetchWithAuth("/ai/knowledge"),
    trainModel: () => fetchWithAuth("/ai/train", { method: "POST" }),
  },
  
  // Market data endpoints
  market: {
    getPriceData: (symbol: string, period: string) => 
      fetchWithAuth(`/market/price?symbol=${symbol}&period=${period}`),
    getCurrentPrice: (symbol: string) => fetchWithAuth(`/market/price/current?symbol=${symbol}`),
  },
  
  // Configuration endpoints
  config: {
    get: () => fetchWithAuth("/config"),
    update: (configData: any) => fetchWithAuth("/config", {
      method: "POST",
      body: JSON.stringify(configData),
    }),
    updateOpenAI: (apiKey: string, endpoint?: string) => fetchWithAuth("/config/openai", {
      method: "POST",
      body: JSON.stringify({ apiKey, endpoint }),
    }),
  },
  
  // System status endpoint
  status: {
    get: () => fetchWithAuth("/status"),
  },
  
  // Test connection to backend
  testConnection: async (): Promise<boolean> => {
    try {
      await fetchWithAuth("/health");
      return true;
    } catch (error) {
      return false;
    }
  }
};
