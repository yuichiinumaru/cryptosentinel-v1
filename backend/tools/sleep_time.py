"""
Toolkit for pre-computing insights during 'sleep-time'.
"""
import logging
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from agno.tools.toolkit import Toolkit
from agno.models.openai import OpenAIChat as LLMClient

from backend.khala_integration import KhalaMemoryToolkit, StoreMemoryInput
from backend.config import Config

logger = logging.getLogger(__name__)

class ThinkAheadInput(BaseModel):
    market_context: str = Field(..., description="A summary of the current market data and news.")
    symbol: str = Field(..., description="The cryptocurrency symbol being analyzed, e.g., BTC.")

class SleepTimeToolkit(Toolkit):
    """
    A toolkit that allows an agent to "think" about a context ahead of time
    and store those thoughts in memory.
    """
    def __init__(self, **kwargs):
        super().__init__(name="sleep_time_toolkit", **kwargs)
        self.register(self.think_ahead)
        self.khala_memory = KhalaMemoryToolkit()
        self.llm_client = LLMClient(id=Config.get_model().id)


    async def think_ahead(self, input: ThinkAheadInput) -> str:
        """
        Analyzes a given market context to generate and store insights,
        potential future scenarios, and key observations that might be useful
        for future queries. This is the 'sleep-time compute' phase.
        """
        prompt = f"""
        You are a proactive financial analyst. Your task is to perform "sleep-time compute".
        You have been given the following market context for {input.symbol.upper()}:
        ---
        {input.market_context}
        ---

        Based on this context, please generate a concise set of "pre-computed thoughts".
        These thoughts should anticipate potential user questions or future market movements.
        Focus on:
        1.  **Key Insights:** What are the most critical takeaways from the data?
        2.  **Potential Scenarios:** What are 2-3 likely future scenarios (e.g., bullish breakout, bearish downturn, consolidation)?
        3.  **Leading Indicators:** What are the most important metrics or news pieces to watch?
        4.  **Actionable Ideas:** What are potential trading or analysis ideas that stem from this context?

        Your output will be stored in a memory system to speed up future analysis. Be clear and concise.
        Structure your response as a list of bullet points.
        """
        try:
            logger.info(f"Generating pre-computed thoughts for {input.symbol.upper()}...")
            response = await self.llm_client.completion(prompt)

            thought_content = response.get_content_as_string()
            if not thought_content:
                return "Failed to generate any thoughts from the LLM."

            # Now, store these thoughts in Khala memory
            store_input = StoreMemoryInput(
                content=f"Pre-computed thoughts for {input.symbol.upper()}:\n{thought_content}",
                importance=0.75,  # Pre-computed thoughts are highly important
                tags=["sleep_time_compute", "pre_computation", input.symbol.lower()]
            )

            store_result = await self.khala_memory.store_memory(store_input)
            logger.info(f"Stored pre-computed thoughts in memory: {store_result}")

            return f"Successfully generated and stored pre-computed thoughts for {input.symbol.upper()}."

        except Exception as e:
            logger.exception("Error during sleep-time computation (think_ahead)")
            return f"An error occurred while generating thoughts: {str(e)}"

# Singleton instance for easy import
sleep_time_toolkit = SleepTimeToolkit()
