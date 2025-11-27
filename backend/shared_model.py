import os
from agno.models.google import Gemini

def get_shared_model():
    """
    Returns a shared instance of the Gemini model.
    The API key is not provided at instantiation, so it must be present
    in the environment (e.g., set by a FastAPI dependency) when the model is used.
    """
    return Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        temperature=float(os.getenv("temperature", 0.7)),
    )
