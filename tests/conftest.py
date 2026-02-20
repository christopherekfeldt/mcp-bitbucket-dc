"""Pytest fixtures for mcp-bitbucket-dc tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_bitbucket_dc.client import BitbucketClient
from mcp_bitbucket_dc.config import BitbucketConfig


@pytest.fixture
def config() -> BitbucketConfig:
    return BitbucketConfig(
        base_url="https://git.example.com",
        api_token="test-token-123",
    )


@pytest.fixture
def mock_client(config: BitbucketConfig) -> MagicMock:
    """A mock BitbucketClient with async methods."""
    client = MagicMock(spec=BitbucketClient)
    client.config = config
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.get_raw = AsyncMock()
    client.get_paged = AsyncMock()
    client.close = AsyncMock()
    return client
