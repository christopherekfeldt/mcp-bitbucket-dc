"""MCP server definition and tool registration for Bitbucket Data Center."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import Context, FastMCP

from .client import BitbucketClient
from .config import BitbucketConfig
from .tools.code_search import register_code_search_tools
from .tools.commits import register_commit_tools
from .tools.files import register_file_tools
from .tools.projects import register_project_tools
from .tools.pull_requests import register_pull_request_tools
from .tools.repositories import register_repository_tools

logger = logging.getLogger(__name__)

# ── Global client (set during lifespan) ─────────────────────────────────────

_client: BitbucketClient | None = None


def get_client(ctx: Context) -> BitbucketClient:
    """Retrieve the BitbucketClient from the server lifespan context."""
    if _client is None:
        raise RuntimeError("BitbucketClient not initialized — server lifespan did not start")
    return _client


# ── Lifespan ────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Initialize BitbucketClient on startup, close on shutdown."""
    global _client
    config = BitbucketConfig.from_env()
    _client = BitbucketClient(config)
    logger.info("Bitbucket DC MCP server started — connected to %s", config.base_url)
    try:
        yield {}
    finally:
        await _client.close()
        _client = None
        logger.info("Bitbucket DC MCP server stopped")


# ── Server instance ────────────────────────────────────────────────────────

mcp = FastMCP(
    name="Bitbucket DC MCP",
    instructions=(
        "MCP server for Bitbucket Data Center. Provides tools to search code, "
        "browse files, manage pull requests, view commits, and explore projects "
        "and repositories. Supports Lucene-style code search with filters like "
        "ext:java, lang:python, repo:name, project:KEY, and boolean operators."
    ),
    lifespan=lifespan,
)

# ── Register all tools ─────────────────────────────────────────────────────

register_project_tools(mcp, get_client)
register_repository_tools(mcp, get_client)
register_pull_request_tools(mcp, get_client)
register_commit_tools(mcp, get_client)
register_code_search_tools(mcp, get_client)
register_file_tools(mcp, get_client)
