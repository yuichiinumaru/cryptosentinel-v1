from agno.agent import Agent
from agno.models.google import Gemini
from typing import Optional
import os

def create_agent(
    name: str,
    role: str,
    instructions_path: str,
    tools: list = [],
    model_id: str = "gemini-1.5-flash-latest",
    temperature: float = 0.7
) -> Agent:
    """
    Factory function to create a fresh Agent instance.
    """
    # Load instructions safely
    if os.path.exists(instructions_path):
        with open(instructions_path, 'r') as f:
            instructions = f.read()
    else:
        instructions = f"You are a {role}."

    return Agent(
        name=name,
        role=role,
        instructions=instructions,
        tools=tools,
        model=Gemini(id=model_id, temperature=temperature),
    )
