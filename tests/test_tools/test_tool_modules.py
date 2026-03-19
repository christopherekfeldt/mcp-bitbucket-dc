"""Tool-level tests for MCP tool modules with mocked API responses."""

import json
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
        self.tool_kwargs = {}

    def tool(self, *args, **kwargs):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            self.tool_kwargs[fn.__name__] = kwargs
            return fn

        return decorator


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
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
async def test_projects_module_tools_json_response(fake_client):
    mcp = FakeMCP()
    register_project_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_paged.return_value = {
        "values": [{"name": "Platform", "key": "PLAT", "public": False}],
        "size": 1,
        "isLastPage": True,
    }

    result = await mcp.tools["bitbucket_get_projects"](ctx=object(), response_format="json")
    payload = json.loads(result)

    assert payload["values"][0]["key"] == "PLAT"
    assert payload["size"] == 1


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
async def test_code_search_module_tools_json_response(fake_client):
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

    result = await mcp.tools["bitbucket_code_search"](
        ctx=object(), query="App", response_format="json"
    )
    payload = json.loads(result)

    assert payload["count"] == 1
    assert payload["values"][0]["file"] == "src/main/App.java"


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
async def test_files_module_tools_json_response(fake_client):
    mcp = FakeMCP()
    register_file_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_raw.return_value = "print('hello')"

    result = await mcp.tools["bitbucket_get_file_content"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        path="src/app.py",
        response_format="json",
    )
    payload = json.loads(result)

    assert payload["path"] == "src/app.py"
    assert payload["content"] == "print('hello')"


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


def test_tool_annotations_include_required_hints():
    mcp = FakeMCP()
    register_project_tools(mcp, lambda _ctx: MagicMock())
    register_repository_tools(mcp, lambda _ctx: MagicMock())
    register_commit_tools(mcp, lambda _ctx: MagicMock())
    register_code_search_tools(mcp, lambda _ctx: MagicMock())
    register_file_tools(mcp, lambda _ctx: MagicMock())
    register_pull_request_tools(mcp, lambda _ctx: MagicMock())

    required = {"readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"}
    for tool_name, kwargs in mcp.tool_kwargs.items():
        annotations = kwargs.get("annotations", {})
        assert required.issubset(annotations.keys()), f"Missing annotation keys for {tool_name}"


def test_write_tools_have_non_readonly_annotations():
    mcp = FakeMCP()
    register_pull_request_tools(mcp, lambda _ctx: MagicMock())

    write_tools = [
        "bitbucket_post_pull_request_comment",
        "bitbucket_create_pull_request",
        "bitbucket_update_pull_request",
        "bitbucket_update_pull_request_comment",
        "bitbucket_delete_pull_request_comment",
    ]

    for tool_name in write_tools:
        annotations = mcp.tool_kwargs[tool_name]["annotations"]
        assert annotations["readOnlyHint"] is False
        assert annotations["destructiveHint"] is True
        assert annotations["idempotentHint"] is False
        assert annotations["openWorldHint"] is True


def test_write_tools_file_module_annotations():
    mcp = FakeMCP()
    register_file_tools(mcp, lambda _ctx: MagicMock())

    annotations = mcp.tool_kwargs["bitbucket_create_branch"]["annotations"]
    assert annotations["readOnlyHint"] is False
    assert annotations["destructiveHint"] is False
    assert annotations["idempotentHint"] is False
    assert annotations["openWorldHint"] is True


# ── New tool tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_commit(fake_client):
    mcp = FakeMCP()
    register_commit_tools(mcp, lambda _ctx: fake_client)

    fake_client.get.return_value = {
        "id": "abcdef1234567890",
        "displayId": "abcdef1234",
        "message": "fix: resolve null pointer\n\nDetailed description here.",
        "author": {"name": "dev", "emailAddress": "dev@example.com"},
        "committer": {"name": "dev", "emailAddress": "dev@example.com"},
        "authorTimestamp": 1700000000000,
        "parents": [{"id": "parent123", "displayId": "parent12"}],
    }

    result = await mcp.tools["bitbucket_get_commit"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        commit_id="abcdef1234567890",
    )

    assert "Commit" in result
    assert "fix: resolve null pointer" in result
    assert "dev" in result
    fake_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_commit_json(fake_client):
    mcp = FakeMCP()
    register_commit_tools(mcp, lambda _ctx: fake_client)

    fake_client.get.return_value = {
        "id": "abcdef1234567890",
        "displayId": "abcdef1234",
        "message": "fix: something",
        "author": {"name": "dev", "emailAddress": "dev@example.com"},
        "committer": {"name": "dev", "emailAddress": "dev@example.com"},
        "authorTimestamp": 1700000000000,
        "parents": [],
    }

    result = await mcp.tools["bitbucket_get_commit"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        commit_id="abcdef1234567890",
        response_format="json",
    )
    payload = json.loads(result)
    assert payload["id"] == "abcdef1234567890"


@pytest.mark.asyncio
async def test_get_commit_diff(fake_client):
    mcp = FakeMCP()
    register_commit_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_raw.return_value = (
        "--- a/src/app.py\n+++ b/src/app.py\n@@ -1,3 +1,4 @@\n+import os\n import sys"
    )

    result = await mcp.tools["bitbucket_get_commit_diff"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        commit_id="abcdef1234",
    )

    assert "Diff for commit" in result
    assert "+import os" in result
    fake_client.get_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_commit_diff_with_path(fake_client):
    mcp = FakeMCP()
    register_commit_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_raw.return_value = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new"

    result = await mcp.tools["bitbucket_get_commit_diff"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        commit_id="abcdef1234",
        path="file.py",
    )

    assert "`file.py`" in result
    fake_client.get_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_repositories(fake_client):
    mcp = FakeMCP()
    register_repository_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_paged.return_value = {
        "values": [
            {
                "name": "backend",
                "slug": "backend",
                "state": "AVAILABLE",
                "project": {"key": "PLAT", "name": "Platform"},
            },
            {
                "name": "frontend",
                "slug": "frontend",
                "state": "AVAILABLE",
                "project": {"key": "PLAT", "name": "Platform"},
            },
        ],
        "size": 2,
        "isLastPage": True,
    }

    result = await mcp.tools["bitbucket_search_repositories"](
        ctx=object(),
        name="end",
    )

    assert "Repositories" in result
    assert "backend" in result
    assert "frontend" in result
    fake_client.get_paged.assert_awaited_once()
    call_args = fake_client.get_paged.call_args
    assert call_args[0][0] == "/rest/api/latest/repos"


@pytest.mark.asyncio
async def test_search_repositories_json(fake_client):
    mcp = FakeMCP()
    register_repository_tools(mcp, lambda _ctx: fake_client)

    fake_client.get_paged.return_value = {
        "values": [
            {
                "name": "backend",
                "slug": "backend",
                "state": "AVAILABLE",
                "project": {"key": "PLAT"},
            }
        ],
        "size": 1,
        "isLastPage": True,
    }

    result = await mcp.tools["bitbucket_search_repositories"](
        ctx=object(),
        response_format="json",
    )
    payload = json.loads(result)
    assert payload["values"][0]["slug"] == "backend"


@pytest.mark.asyncio
async def test_update_pull_request_comment(fake_client):
    mcp = FakeMCP()
    register_pull_request_tools(mcp, lambda _ctx: fake_client)

    fake_client.put.return_value = {"id": 100, "version": 2, "text": "Updated text"}

    result = await mcp.tools["bitbucket_update_pull_request_comment"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        pull_request_id=42,
        comment_id=100,
        version=1,
        text="Updated text",
    )

    assert "updated successfully" in result
    assert "100" in result
    fake_client.put.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_pull_request_comment(fake_client):
    mcp = FakeMCP()
    register_pull_request_tools(mcp, lambda _ctx: fake_client)

    fake_client.delete.return_value = {}

    result = await mcp.tools["bitbucket_delete_pull_request_comment"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        pull_request_id=42,
        comment_id=100,
        version=1,
    )

    assert "deleted successfully" in result
    assert "100" in result
    fake_client.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_branch(fake_client):
    mcp = FakeMCP()
    register_file_tools(mcp, lambda _ctx: fake_client)

    fake_client.post.return_value = {
        "id": "refs/heads/feature/new-thing",
        "displayId": "feature/new-thing",
        "type": "BRANCH",
        "latestCommit": "abcdef123456",
        "isDefault": False,
    }

    result = await mcp.tools["bitbucket_create_branch"](
        ctx=object(),
        project_key="PLAT",
        repository_slug="backend",
        name="feature/new-thing",
        start_point="main",
    )

    assert "feature/new-thing" in result
    assert "created successfully" in result
    fake_client.post.assert_awaited_once()
    call_body = fake_client.post.call_args[1]["json"]
    assert call_body["name"] == "feature/new-thing"
    assert call_body["startPoint"] == "main"
