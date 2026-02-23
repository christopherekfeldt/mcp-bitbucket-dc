"""Commit-related MCP tools."""

from typing import Annotated, Optional

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import format_commits


def register_commit_tools(mcp, get_client) -> None:
    """Register commit tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get Commits", "readOnlyHint": True},
    )
    async def bitbucket_get_commits(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        path: Annotated[
            Optional[str],
            Field(description="Filter commits affecting this file path"),
        ] = None,
        since: Annotated[
            Optional[str],
            Field(description="Commit hash or ref — exclude commits reachable from this"),
        ] = None,
        until: Annotated[
            Optional[str],
            Field(
                description="Commit hash or ref — include commits reachable from this (default: default branch HEAD)"
            ),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-100)", ge=1, le=100)] = 25,
    ) -> str:
        """Get commits for a repository.

        Lists commits in reverse chronological order. Use `since`/`until` to specify
        a commit range (like git log since..until). Use `path` to only show commits
        that modified a specific file.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if path:
            params["path"] = path
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/commits",
            params=params,
            start=start,
            limit=limit,
        )
        return format_commits(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )
