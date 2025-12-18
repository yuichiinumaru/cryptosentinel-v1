from functools import wraps
from agno.tools.toolkit import Toolkit
from backend.agentspec.enforcement import AgentSpecEnforcement

def apply_enforcement_to_toolkit(toolkit: Toolkit, enforcement_engine: AgentSpecEnforcement) -> Toolkit:
    """
    Wraps all public methods of a toolkit with the AgentSpec enforcement logic.
    """
    for attr_name in dir(toolkit):
        if not attr_name.startswith('_'):
            attr = getattr(toolkit, attr_name)
            if callable(attr) and hasattr(attr, '__call__'):
                setattr(toolkit, attr_name, _wrap_method(attr, enforcement_engine))
    return toolkit

def _wrap_method(method: callable, enforcement_engine: AgentSpecEnforcement):
    @wraps(method)
    def wrapped_method(*args, **kwargs):
        trigger_name = method.__name__
        agent_context = {'args': args, 'kwargs': kwargs}
        enforcement_engine.enforce(trigger_name, agent_context)
        return method(*args, **kwargs)
    return wrapped_method
