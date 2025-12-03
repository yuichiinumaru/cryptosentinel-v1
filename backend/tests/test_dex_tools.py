import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.dex import DexToolkit, ExecuteSwapInput, RevokeApprovalInput, ExecuteTransactionSimulationInput

def test_dex_toolkit_mock():
    toolkit = DexToolkit()

from tools.dex import execute_swap, revoke_approval, execute_transaction_simulation
from tools.dex import ExecuteSwapInput, RevokeApprovalInput, ExecuteTransactionSimulationInput

def test_dex_tools_mock():
    # Test ExecuteSwap (Mock)
    swap_input = ExecuteSwapInput(
        token_in="0x1111111111111111111111111111111111111111",
        token_out="0x2222222222222222222222222222222222222222",
        amount_in=1.0,
        chain="ethereum",
        dex="uniswap_v2"
    )
    # Using the method directly
    swap_output = toolkit.execute_swap(swap_input)
    swap_output = execute_swap.entrypoint(swap_input)
    print(f"Swap Output: {swap_output}")
    assert swap_output.success == True
    assert "MOCK" in swap_output.tx_hash

    # Test RevokeApproval (Mock)
    revoke_input = RevokeApprovalInput(
        token_address="0x1111111111111111111111111111111111111111",
        spender_address="0x3333333333333333333333333333333333333333",
        chain="ethereum"
    )
    revoke_output = toolkit.revoke_approval(revoke_input)
    revoke_output = revoke_approval.entrypoint(revoke_input)
    print(f"Revoke Output: {revoke_output}")
    assert revoke_output.success == True
    assert "MOCK" in revoke_output.tx_hash

    # Test Simulation (Mock)
    sim_input = ExecuteTransactionSimulationInput(
        token_in="0x1111111111111111111111111111111111111111",
        token_out="0x2222222222222222222222222222222222222222",
        amount_in=1.0
    )
    sim_output = toolkit.execute_transaction_simulation(sim_input)
    sim_output = execute_transaction_simulation.entrypoint(sim_input)
    print(f"Simulation Output: {sim_output}")
    assert sim_output.success == True
    assert sim_output.simulated_amount_out > 0

if __name__ == "__main__":
    try:
        test_dex_toolkit_mock()
        test_dex_tools_mock()
        print("All mock tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
