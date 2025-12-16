
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.khala_integration import KhalaMemoryToolkit, SearchMemoryInput, StoreMemoryInput

@pytest.fixture
def mock_surreal_client():
    with patch("backend.khala_integration.get_surreal_client") as mock_get:
        client_mock = AsyncMock()
        mock_get.return_value = client_mock
        yield client_mock

@pytest.mark.asyncio
async def test_search_memory(mock_surreal_client):
    toolkit = KhalaMemoryToolkit()

    # Mock return value
    mock_surreal_client.search_memories_by_bm25.return_value = [
        {"content": "Bitcoin is volatile", "created_at": "2023-10-01"},
        {"content": "ETH is rising", "created_at": "2023-10-02"}
    ]

    input_data = SearchMemoryInput(query="crypto", top_k=2)
    result = await toolkit.search_memory(input_data)

    assert "Bitcoin is volatile" in result
    assert "ETH is rising" in result
    mock_surreal_client.search_memories_by_bm25.assert_called_once()

@pytest.mark.asyncio
async def test_store_memory(mock_surreal_client):
    toolkit = KhalaMemoryToolkit()

    mock_surreal_client.create_memory.return_value = "memory:123"

    input_data = StoreMemoryInput(content="New strategy", importance=0.8, tags=["strategy"])
    result = await toolkit.store_memory(input_data)

    assert "memory:123" in result
    mock_surreal_client.create_memory.assert_called_once()
