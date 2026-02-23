"""Tool-level tests for MCP tool modules with mocked API responses."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_bitbucket_dc.tools.code_search import register_code_search_tools
from mcp_bitbucket_dc.tools.commits import register_commit_tools
from mcp_bitbucket_dc.tools.files import register_file_tools
from mcp_bitbucket_dc.tools.projects import register_project_tools
from mcp_bitbucket_dc.tools.pull_requests import register_pull_request_tools
from mcp_bitbucket_dc.tools.repositories import register_repository_tools


class FakeMCP:
    """Minimal MCP stand-in for collecting registered tool callables."""

    def __init__(self):
        self.tools = {}

    def tool(self, *args, **kwargs):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.get_raw = AsyncMock()
    client.get_paged = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_projects_module_tools(fake_client):
    mcp = FakeMCP()
    register_project_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_paged.return_value = {
        "values": [{"name": "Platform", "key": "PLAT", "public": False}],
        "size": 1,
        "isLastPage": True,
    }

    result = await mcp.tools["bitbucket_get_projects"](ctx=object())

    assert "Projects" in result
    assert "Platform" in result
    fake_client.get_paged.assert_awaited_once()


@pytest.mark.asyncio
async def test_repositories_module_tools(fake_client):
    mcp = FakeMCP()
    register_repository_tools(mcp, lambda _ctx: fake_client)

    fake_client.get.return_value = {
        "name": "backend",
        "slug": "backend",
        "state": "AVAILABLE",
        "forkable": True,
        "public": False,
        "archived": False,
        "project": {"name": "Platform", "key": "PLAT"},
    }

    result = await mcp.tools["bitbucket_get_repository"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
    )

    assert "backend" in result
    fake_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_commits_module_tools(fake_client):
    mcp = FakeMCP()
    register_commit_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_paged.return_value = {
        "values": [
            {
                "id": "1234567890abcdef",
                "displayId": "1234567890ab",
                "message": "feat: add endpoint",
                "author": {"name": "dev"},
                "authorTimestamp": 1700000000000,
            }
        ],
        "size": 1,
        "isLastPage": True,
    }

    result = await mcp.tools["bitbucket_get_commits"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
    )

    assert "Commits" in result
    assert "feat: add endpoint" in result
    fake_client.get_paged.assert_awaited_once()


@pytest.mark.asyncio
async def test_code_search_module_tools(fake_client):
    mcp = FakeMCP()
    register_code_search_tools(mcp, lambda _ctx: fake_client)

    fake_client.post.return_value = {
        "code": {
            "values": [
                {
                    "repository": {"name": "backend", "project": {"key": "PLAT"}},
                    "file": "src/main/App.java",
                    "hitCount": 1,
                    "hitContexts": [[{"line": 10, "text": "class <em>App</em>"}]],
                }
            ],
            "count": 1,
            "isLastPage": True,
        }
    }

    result = await mcp.tools["bitbucket_code_search"](ctx=object(), query="App")

    assert "Search Results" in result
    assert "src/main/App.java" in result
    fake_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_files_module_tools(fake_client):
    mcp = FakeMCP()
    register_file_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_raw.return_value = "print('hello')"

    result = await mcp.tools["bitbucket_get_file_content"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        path="src/app.py",
    )

    assert "# File: `src/app.py`" in result
    assert "print('hello')" in result
    fake_client.get_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_pull_requests_module_tools(fake_client):
    mcp = FakeMCP()
    register_pull_request_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_paged.return_value = {
        "values": [
            {
                "id": 42,
                "state": "OPEN",
                "title": "feat: improve search",
                "updatedDate": 1700000000000,
                "author": {"user": {"displayName": "Dev User"}},
                "fromRef": {"displayId": "feature/search"},
                "toRef": {"displayId": "main"},
            }
        ],
        "size": 1,
        "isLastPage": True,
    }

    result = await mcp.tools["bitbucket_get_pull_requests"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
    )

    assert "Pull Requests" in result
    assert "feat: improve search" in result
    fake_client.get_paged.assert_awaited_once()
