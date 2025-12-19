from agno.tools.toolkit import Toolkit
from backend.paper_implementations.cope_agent import CopeAgent

class CopeToolkit(Toolkit):
    def __init__(self, session_id: str):
        super().__init__()
        self._session_id = session_id
        self._cope_agent = None

    @property
    def cope_agent(self):
        if self._cope_agent is None:
            self._cope_agent = CopeAgent(self._session_id)
        return self._cope_agent

    def analyze_task(self, task: str) -> str:
        """
        Analyzes a trading task using a multi-round, collaborative process
        with small and large models to determine the best course of action.
        """
        return self.cope_agent.reason(task)

def get_cope_toolkit(session_id: str) -> CopeToolkit:
    return CopeToolkit(session_id)
