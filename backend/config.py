import os
import random
from typing import Optional
from dotenv import load_dotenv
from agno.models.google import Gemini

load_dotenv()

class Config:
    """
    Centralized configuration management.
    Enforces "Zero Fragility" by validating inputs and handling secrets securely.
    """

    @staticmethod
    def get_model(id: str = None, temperature: float = None) -> Gemini:
        """
        Returns a configured Gemini model instance with key rotation.
        """
        _id = id or os.getenv("gemini_model", "gemini-1.5-flash-latest")

        # Safe float conversion
        try:
            _temperature = temperature if temperature is not None else float(os.getenv("temperature", 0.7))
        except ValueError:
            raise ValueError("CRITICAL: 'temperature' env var must be a float.")

        # Key Rotation Logic
        keys_str = os.getenv("gemini_api_keys")
        api_key: Optional[str] = None

        if keys_str:
            keys = [k.strip() for k in keys_str.split(',') if k.strip()]
            if keys:
                api_key = random.choice(keys) # Actual rotation (Random Load Balancing)

        if not api_key:
             # Fallback to single key
             api_key = os.getenv("gemini_api_key")

        if not api_key:
            raise ValueError("CRITICAL: Missing Gemini API Key. Set 'gemini_api_keys' (comma-separated) or 'gemini_api_key'.")

        return Gemini(
            id=_id,
            api_key=api_key,
            temperature=_temperature,
        )

# Removed module-level singleton 'shared_model' to prevent side effects on import.
# Agents must request a model instance.
