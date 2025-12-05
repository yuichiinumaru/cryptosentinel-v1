import pytest
from backend.tools.dex import DexToolkit, ExecuteSwapInput, SimulationInput

def test_dex_toolkit_structure():
    """
    Verifies that the DexToolkit class and models are correctly defined.
    """
    assert DexToolkit is not None
    assert ExecuteSwapInput is not None
    assert SimulationInput is not None

    # Ensure tool registration
    toolkit = DexToolkit()
    # Check if tools are registered (Agno Toolkit stores them in .tools usually)
    # The internal structure might vary, but basic instantiation shouldn't crash.
    assert hasattr(toolkit, "tools") or hasattr(toolkit, "get_tools")
