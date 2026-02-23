"""File browsing, content, and branch/tag MCP tools."""

from typing import Annotated, Literal, Optional

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import (
    format_branches,
    format_browse,
    format_file_list,
    format_tags,
    render_response,
)


def register_file_tools(mcp, get_client) -> None:
    """Register file browsing and branch/tag tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Browse Files",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_browse(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        path: Annotated[
            Optional[str],
            Field(description="Path to browse (e.g. 'src/main/java'). Leave empty for root."),
        ] = None,
        at: Annotated[
            Optional[str],
            Field(description="Branch, tag, or commit to browse at (default: default branch)"),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-1000)", ge=1, le=1000)] = 500,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Browse the file tree of a repository.

        Lists files and directories at the given path. If `path` points to a file,
        returns its content instead. Use `at` to browse a specific branch or commit.
        """
        client: BitbucketClient = get_client(ctx)
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/browse"
        if path:
            endpoint = f"{endpoint}/{path}"
        params: dict = {}
        if at:
            params["at"] = at
        data = await client.get_paged(endpoint, params=params, start=start, limit=limit)
        markdown = format_browse(data, path or "/")
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get File Content",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_file_content(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        path: Annotated[str, Field(description="File path (e.g. 'src/main/App.java')")],
        at: Annotated[
            Optional[str],
            Field(description="Branch, tag, or commit (default: default branch)"),
        ] = None,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Get the raw content of a file from a repository.

        Returns the full file content as text. Use `at` to fetch from a specific
        branch, tag, or commit hash.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if at:
            params["at"] = at
        content = await client.get_raw(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/raw/{path}",
            params=params,
        )
        # Determine file extension for syntax highlighting
        ext = path.rsplit(".", 1)[-1] if "." in path else ""
        markdown = f"# File: `{path}`\n\n```{ext}\n{content}\n```"
        data = {"path": path, "at": at, "content": content}
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "List Files",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_list_files(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        path: Annotated[
            Optional[str],
            Field(description="Sub-path to list from (default: repository root)"),
        ] = None,
        at: Annotated[
            Optional[str],
            Field(description="Branch, tag, or commit (default: default branch)"),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-5000)", ge=1, le=5000)] = 500,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Recursively list all file paths in a repository or sub-directory.

        Returns a flat list of all file paths (no directories). Useful for
        understanding the project structure or finding files by name.
        """
        client: BitbucketClient = get_client(ctx)
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/files"
        if path:
            endpoint = f"{endpoint}/{path}"
        params: dict = {}
        if at:
            params["at"] = at
        data = await client.get_paged(endpoint, params=params, start=start, limit=limit)
        markdown = format_file_list(
            data.get("values", []),
            path=path or "/",
            total=data.get("size", len(data.get("values", []))),
            is_last=data.get("isLastPage", True),
        )
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Branches",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_branches(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        filter_text: Annotated[
            Optional[str],
            Field(description="Filter branches by name (substring match)"),
        ] = None,
        order_by: Annotated[
            Optional[str],
            Field(description="ALPHABETICAL or MODIFICATION (default: MODIFICATION)"),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-1000)", ge=1, le=1000)] = 25,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """List branches in a repository.

        Returns branches with their latest commit hash. Use `filter_text` to search
        for branches by name.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {"details": "true"}
        if filter_text:
            params["filterText"] = filter_text
        if order_by:
            params["orderBy"] = order_by
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/branches",
            params=params,
            start=start,
            limit=limit,
        )
        markdown = format_branches(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Tags",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_tags(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        filter_text: Annotated[
            Optional[str],
            Field(description="Filter tags by name (substring match)"),
        ] = None,
        order_by: Annotated[
            Optional[str],
            Field(description="ALPHABETICAL or MODIFICATION"),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-1000)", ge=1, le=1000)] = 25,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """List tags in a repository.

        Returns tags with their associated commit hash. Use `filter_text` to search
        for tags by name.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if filter_text:
            params["filterText"] = filter_text
        if order_by:
            params["orderBy"] = order_by
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/tags",
            params=params,
            start=start,
            limit=limit,
        )
        markdown = format_tags(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )
        return render_response(response_format, markdown, data)
