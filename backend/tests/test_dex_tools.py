import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.tools.dex import DexToolkit, ExecuteSwapInput

class TestDexToolkit(unittest.IsolatedAsyncioTestCase):
    async def test_execute_swap_async(self):
        toolkit = DexToolkit()

        with patch('backend.tools.dex.Web3Provider.get_async_w3') as mock_get_w3, \
             patch('os.getenv', return_value="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"):

            mock_w3 = AsyncMock()
            mock_get_w3.return_value = mock_w3
            mock_w3.is_connected.return_value = True

            # Sync Mocks
            mock_w3.to_checksum_address = MagicMock(side_effect=lambda x: x)
            mock_w3.eth.account.from_key = MagicMock(return_value=MagicMock(address="0xUser", key=b'key'))

            # Async Mocks for awaitable properties/methods
            # The issue is `await w3.eth.gas_price`.
            # In unittest, `mock_w3.eth.gas_price` is an AsyncMock.
            # Awaiting it should work IF we don't set a return_value that breaks it.
            # But earlier we saw "object AsyncMock can't be used in 'await' expression"??
            # This happens if we mocked it incorrectly or if Python 3.12 has specific behavior for awaiting Mocks.
            # Let's assume w3.eth.gas_price is a PROPERTY that returns an int (awaited automatically?)
            # OR it's an awaitable object.

            # FIX: If code does `await w3.eth.gas_price`, we can mock `gas_price` as a Coroutine.
            async def get_gas_price():
                return 1000000000

            # We assign this coroutine (or property returning it) to gas_price?
            # No, `await mock` works if mock is AsyncMock.
            # Why did it fail? "TypeError: object AsyncMock can't be used in 'await' expression".
            # This suggests `w3.eth` is NOT an AsyncMock, or something is messed up.
            # `mock_w3` is AsyncMock. `mock_w3.eth` is AsyncMock (auto-created).
            # `mock_w3.eth.gas_price` is AsyncMock.
            # Awaiting an AsyncMock works in 3.8+, calls it.
            # EXCEPT if we assigned something weird to it?
            # Let's explicitly set it to a MagicMock that is NOT async, but returns a Future?
            # Or better, just make it a PropertyMock that returns a coroutine.

            # Actually, let's try just setting side_effect to return value, ensuring it's callable.
            # But gas_price is property access, not call. `await w3.eth.gas_price` (no parens).
            # So `w3.eth.gas_price` must evaluate to an Awaitable.

            # Let's set it to a simple Awaitable (Coroutine)
            # mock_w3.eth.gas_price = get_gas_price() # (Removed to avoid RuntimeWarning: never awaited)
            # But `await coroutine` works once. If code calls it twice, second await fails (cannot reuse coroutine).
            # Code calls it multiple times.

            # So `w3.eth.gas_price` must be re-readable.
            # This implies proper MagicMock behavior for property access is needed.
            # But unittest.mock doesn't support "async property" easily.
            # Workaround: Mock the property to return a NEW coroutine each access.

            # We can use a class to mock eth
            class MockEth:
                account = MagicMock()
                contract = MagicMock()
                get_transaction_count = AsyncMock(return_value=0)
                send_raw_transaction = AsyncMock(return_value=b'\x00'*32)
                wait_for_transaction_receipt = AsyncMock(return_value={'status': 1})

                @property
                def gas_price(self):
                    async def _gp(): return 1000000000
                    return _gp()

            mock_w3.eth = MockEth()
            mock_w3.eth.account.from_key.return_value = MagicMock(address="0xUser", key=b'key')

            # Contract setup
            mock_contract = MagicMock()
            def create_async_function_mock(return_value):
                func_wrapper = MagicMock()
                func_wrapper.call = AsyncMock(return_value=return_value)
                func_wrapper.build_transaction = AsyncMock(return_value={'data': '0x', 'to': '0xRouter', 'value': 0, 'gas': 200000, 'gasPrice': 1000000000, 'nonce': 0, 'chainId': 1})
                return func_wrapper

            mock_contract.functions.decimals.return_value = create_async_function_mock(18)
            mock_contract.functions.allowance.return_value = create_async_function_mock(10**30)
            mock_contract.functions.approve.return_value = create_async_function_mock(True)
            mock_contract.functions.getAmountsOut.return_value = create_async_function_mock([100, 90])
            mock_contract.functions.swapExactTokensForTokens.return_value = create_async_function_mock([])

            mock_w3.eth.contract.return_value = mock_contract

            input_data = ExecuteSwapInput(
                token_in="0xTokenA",
                token_out="0xTokenB",
                amount_in=1.0
            )

            output = await toolkit.execute_swap(input_data)

            if not output.success:
                print(f"DEBUG ERROR: {output.error}")

            self.assertTrue(output.success)
            self.assertTrue(len(output.tx_hash) > 0)

if __name__ == "__main__":
    unittest.main()
