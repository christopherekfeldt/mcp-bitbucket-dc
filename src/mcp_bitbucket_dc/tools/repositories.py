"""Repository-related MCP tools."""

from __future__ import annotations

from typing import Annotated, Optional

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import format_repositories, format_repository_detail


def register_repository_tools(mcp, get_client) -> None:
    """Register repository tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get Repositories", "readOnlyHint": True},
    )
    async def bitbucket_get_repositories(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key (e.g. 'PROJ')")],
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results to return (1-1000)", ge=1, le=1000)] = 25,
    ) -> str:
        """Get repositories for a Bitbucket project.

        Lists all repositories within the specified project that the authenticated
        user has access to.
        """
        client: BitbucketClient = get_client(ctx)
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos",
            start=start,
            limit=limit,
        )
        return format_repositories(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get Repository", "readOnlyHint": True},
    )
    async def bitbucket_get_repository(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key (e.g. 'PROJ')")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
    ) -> str:
        """Get details of a specific repository including clone URLs and configuration."""
        client: BitbucketClient = get_client(ctx)
        data = await client.get(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
        )
        return format_repository_detail(data)
