
import { toast } from "@/components/ui/use-toast";

// Base API URL
const DEFAULT_API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Get the configured API URL from sessionStorage or use default
 */
export const getApiUrl = (): string => {
  return sessionStorage.getItem("apiUrl") || DEFAULT_API_URL;
};

/**
 * Set the API URL in sessionStorage
 */
export const setApiUrl = (url: string): void => {
  sessionStorage.setItem("apiUrl", url);
};

/**
 * Get the API key from sessionStorage
 * SECURITY NOTE: Storing keys in JS-accessible storage is risky (XSS).
 * The "Immortal" fix requires HttpOnly cookies, which needs a backend /login endpoint.
 * For now, we use sessionStorage (cleared on tab close) as a mitigation over localStorage.
 */
export const getApiKey = (): string | null => {
  return sessionStorage.getItem("openaiApiKey");
};

/**
 * Set the API key
 */
export const setApiKey = (key: string): void => {
  sessionStorage.setItem("openaiApiKey", key);
}

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
    updateOpenAI: (apiKey: string, endpoint?: string) => {
        setApiKey(apiKey);
        return Promise.resolve({ success: true });
    },
  },
  
  // System status endpoint
  status: {
    get: () => fetchWithAuth("/status"),
  },

  // Chat endpoint
  chat: async (
    message: string,
    onChunk: (chunk: string) => void,
    onClose: () => void
  ) => {
    const apiUrl = getApiUrl();
    const apiKey = getApiKey();

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
        },
        body: JSON.stringify({ message }),
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }

      // Backend returns JSON, not stream.
      // Fix: Read JSON directly.
      const data = await response.json();
      if (data.response) {
          onChunk(data.response);
      }
      onClose();

    } catch (error) {
      console.error("Chat API request failed:", error);
      toast({
        title: "Chat Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
      onClose();
    }
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
