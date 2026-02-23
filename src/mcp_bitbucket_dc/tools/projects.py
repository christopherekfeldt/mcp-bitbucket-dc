"""Project-related MCP tools."""

from typing import Annotated, Literal, Optional

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import format_project, format_projects, render_response


def register_project_tools(mcp, get_client) -> None:
    """Register project tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Projects",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_projects(
        ctx: Context,
        name: Annotated[
            Optional[str], Field(description="Filter projects by name (substring match)")
        ] = None,
        permission: Annotated[
            Optional[str],
            Field(description="Filter by permission: PROJECT_VIEW, PROJECT_ADMIN, REPO_READ, etc."),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[
            int, Field(description="Max results to return (1-1000)", ge=1, le=1000)
        ] = 25,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Get a list of Bitbucket projects.

        Returns projects the authenticated user has access to. Use `name` to filter
        by project name, and `permission` to filter by access level.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if name:
            params["name"] = name
        if permission:
            params["permission"] = permission
        data = await client.get_paged(
            "/rest/api/latest/projects", params=params, start=start, limit=limit
        )
        markdown = format_projects(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Project",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_project(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key (e.g. 'PROJ')")],
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Get details of a specific Bitbucket project by its key."""
        client: BitbucketClient = get_client(ctx)
        data = await client.get(f"/rest/api/latest/projects/{project_key}")
        markdown = format_project(data)
        return render_response(response_format, markdown, data)
