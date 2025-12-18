from agno.tools.toolkit import Toolkit
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from backend.agentspec.parser import AgentSpecParser
from backend.agentspec.enforcement import AgentSpecEnforcement

class AgentSpecTool(Toolkit):
    def __init__(self, enforcement_engine: AgentSpecEnforcement, **kwargs):
        super().__init__(name="agentspec_tool", **kwargs)
        self.enforcement_engine = enforcement_engine
        self.register(self.reload_rules)

    class ReloadRulesInput(BaseModel):
        rules_filepath: str

    def reload_rules(self, input: ReloadRulesInput) -> str:
        """
        Reloads the AgentSpec rules from a specified file.
        """
        try:
            with open(input.rules_filepath, 'r') as f:
                rule_string = f.read()

            parser = AgentSpecParser()
            parsed_rules = parser.parse(rule_string)
            self.enforcement_engine.rules = parsed_rules
            return "AgentSpec rules reloaded successfully."
        except FileNotFoundError:
            return "Error: Rules file not found."
        except Exception as e:
            return f"An error occurred while reloading rules: {e}"

def create_agentspec_tool(enforcement_engine: AgentSpecEnforcement) -> AgentSpecTool:
    return AgentSpecTool(enforcement_engine=enforcement_engine)
