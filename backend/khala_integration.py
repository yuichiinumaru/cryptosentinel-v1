"""
Integration module for Khala Memory System.
Provides the KhalaMemoryToolkit for agents to interact with long-term memory.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from agno.tools.toolkit import Toolkit

# Import from khala-memory
try:
    from khala.infrastructure.surrealdb.client import SurrealDBClient
    from khala.domain.memory.entities import Memory, MemoryTier, ImportanceScore
except ImportError as e:
    # Fallback if khala is not installed or path issues
    logging.warning(f"Failed to import Khala components: {e}")
    SurrealDBClient = None

logger = logging.getLogger(__name__)

# Lazy singleton
_surreal_client: Optional[Any] = None

def get_surreal_client() -> Any:
    global _surreal_client
    if SurrealDBClient is None:
        return None

    if _surreal_client is None:
        # Default configuration
        _surreal_client = SurrealDBClient(
            url=os.getenv("SURREALDB_URL", "ws://localhost:8000/rpc"),
            namespace=os.getenv("SURREALDB_NAMESPACE", "khala"),
            database=os.getenv("SURREALDB_DATABASE", "memories"),
            username=os.getenv("SURREALDB_USER", "root"),
            password=os.getenv("SURREALDB_PASS", "root")
        )
    return _surreal_client

class SearchMemoryInput(BaseModel):
    query: str = Field(..., description="The query to search for in memory.")
    top_k: int = Field(5, description="Number of results to return.")

class StoreMemoryInput(BaseModel):
    content: str = Field(..., description="The content to store.")
    importance: float = Field(0.5, description="Importance score (0.0 to 1.0).")
    tags: List[str] = Field(default_factory=list, description="Tags for the memory.")

class StoreMarketSituationInput(BaseModel):
    symbol: str = Field(..., description="The asset symbol (e.g., bitcoin).")
    regime: str = Field(..., description="Market regime (e.g., Bull, Bear).")
    trend: str = Field(..., description="Trend direction.")
    summary: str = Field(..., description="Brief summary of the situation.")

class KhalaMemoryToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="khala_memory", **kwargs)
        if SurrealDBClient:
            self.register(self.search_memory)
            self.register(self.store_memory)
            self.register(self.store_market_situation)
        else:
            logger.warning("KhalaMemoryToolkit initialized but Khala library is missing.")

    async def search_memory(self, input: SearchMemoryInput) -> str:
        """Search the long-term memory for relevant information using BM25 text search."""
        client = get_surreal_client()
        if not client:
            return "Memory system is unavailable."

        try:
            # Note: User ID context should ideally come from the agent context
            results = await client.search_memories_by_bm25(
                query_text=input.query,
                user_id="default_user",
                top_k=input.top_k
            )

            if not results:
                return "No relevant memories found."

            formatted_results = []
            for res in results:
                content = res.get('content', '')
                date = res.get('created_at', 'unknown')
                formatted_results.append(f"- [{date}] {content}")

            return "Found memories:\n" + "\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            # Fail gracefully so the agent doesn't crash
            return f"Error searching memory: {str(e)}"

    async def store_memory(self, input: StoreMemoryInput) -> str:
        """Store a new memory in the long-term storage."""
        client = get_surreal_client()
        if not client:
            return "Memory system is unavailable."

        try:
            memory = Memory(
                user_id="default_user",
                content=input.content,
                tier=MemoryTier.WORKING,
                importance=ImportanceScore(input.importance),
                tags=input.tags
            )

            memory_id = await client.create_memory(memory)
            return f"Memory stored successfully with ID: {memory_id}"
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return f"Error storing memory: {str(e)}"

    async def store_market_situation(self, input: StoreMarketSituationInput) -> str:
        """Stores a structured snapshot of the market situation."""
        content = f"MARKET SITUATION for {input.symbol.upper()}: Regime={input.regime}, Trend={input.trend}.\nSummary: {input.summary}"

        # We delegate to store_memory
        # Importance 0.8 because market context is high value
        store_input = StoreMemoryInput(
            content=content,
            importance=0.8,
            tags=["market_situation", input.symbol.lower(), input.regime.lower()]
        )
        return await self.store_memory(store_input)
