import os
from dotenv import load_dotenv
from agno.models.google import Gemini

load_dotenv()

class Config:
    @staticmethod
    def get_model(id: str = None, temperature: float = None):
        """Returns a configured Gemini model instance."""
        _id = id or os.getenv("gemini_model", "gemini-1.5-flash-latest")
        _temperature = temperature or float(os.getenv("temperature", 0.7))

        # Simple key rotation logic could go here, or reusing the KeyManager from agents.py
        # For now, simplistic implementation to support standardizing agents.
        keys_str = os.getenv("gemini_api_keys")
        api_key = keys_str.split(',')[0].strip() if keys_str else None

        if not api_key:
             # Fallback to single key if available
             api_key = os.getenv("gemini_api_key")

        return Gemini(
            id=_id,
            api_key=api_key,
            temperature=_temperature,
        )

# Singleton instance for simple use cases
shared_model = Config.get_model()
