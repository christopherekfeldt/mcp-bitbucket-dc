"""Tests for BitbucketClient error handling and request helpers."""

import httpx
import pytest

from mcp_bitbucket_dc.client import BitbucketClient, BitbucketClientError
from mcp_bitbucket_dc.config import BitbucketConfig


@pytest.fixture
def client() -> BitbucketClient:
    config = BitbucketConfig(base_url="https://git.example.com", api_token="token")
    return BitbucketClient(config)


def _response(status_code: int, json_body: dict | None = None, text: str = "") -> httpx.Response:
    request = httpx.Request("GET", "https://git.example.com/rest/api/latest/test")
    if json_body is not None:
        return httpx.Response(status_code=status_code, request=request, json=json_body)
    return httpx.Response(status_code=status_code, request=request, text=text)


def test_check_errors_401(client: BitbucketClient):
    response = _response(401, json_body={"errors": [{"message": "bad token"}]})
    with pytest.raises(BitbucketClientError, match="Authentication failed"):
        client._check_errors(response)


def test_check_errors_403(client: BitbucketClient):
    response = _response(403, json_body={"message": "forbidden"})
    with pytest.raises(BitbucketClientError, match="Permission denied"):
        client._check_errors(response)


def test_check_errors_404(client: BitbucketClient):
    response = _response(404, json_body={"message": "repo not found"})
    with pytest.raises(BitbucketClientError, match="Not found"):
        client._check_errors(response)


def test_check_errors_500_uses_error_messages(client: BitbucketClient):
    response = _response(500, json_body={"errors": [{"message": "server exploded"}]})
    with pytest.raises(BitbucketClientError, match="server exploded"):
        client._check_errors(response)


def test_handle_response_204_returns_empty_dict(client: BitbucketClient):
    response = _response(204, text="")
    assert client._handle_response(response) == {}


@pytest.mark.asyncio
async def test_get_paged_merges_params(client: BitbucketClient, monkeypatch):
    captured: dict = {}

    async def fake_get(path: str, params: dict | None = None):
        captured["path"] = path
        captured["params"] = params
        return {"ok": True}

    monkeypatch.setattr(client, "get", fake_get)

    result = await client.get_paged(
        "/rest/api/latest/projects/PROJ/repos",
        params={"filterText": "api"},
        start=50,
        limit=10,
    )

    assert result == {"ok": True}
    assert captured["path"] == "/rest/api/latest/projects/PROJ/repos"
    assert captured["params"] == {"filterText": "api", "start": 50, "limit": 10}


@pytest.mark.asyncio
async def test_close_client(client: BitbucketClient):
    await client.close()
