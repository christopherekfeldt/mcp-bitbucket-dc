"""Commit-related MCP tools."""

from typing import Annotated, Literal, Optional

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import format_commit_detail, format_commits, render_response


def register_commit_tools(mcp, get_client) -> None:
    """Register commit tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Commits",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
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
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
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
        markdown = format_commits(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Commit",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_commit(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        commit_id: Annotated[str, Field(description="The commit hash (full or abbreviated)")],
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Get full details of a single commit including message, author, and parents."""
        client: BitbucketClient = get_client(ctx)
        data = await client.get(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/commits/{commit_id}"
        )
        markdown = format_commit_detail(data)
        return render_response(response_format, markdown, data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Get Commit Diff",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_get_commit_diff(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        commit_id: Annotated[str, Field(description="The commit hash (full or abbreviated)")],
        path: Annotated[
            Optional[str],
            Field(description="Restrict diff to a specific file path"),
        ] = None,
        context_lines: Annotated[
            Optional[int],
            Field(description="Number of context lines around changes (default: 10)"),
        ] = None,
        whitespace: Annotated[
            Optional[str],
            Field(description="Whitespace handling: SHOW, IGNORE_ALL, or IGNORE_TRAILING"),
        ] = None,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Get the diff for a specific commit.

        Returns the unified diff showing all changes introduced by the commit.
        Optionally restrict to a single file with `path`.
        """
        client: BitbucketClient = get_client(ctx)
        endpoint = (
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/commits/{commit_id}/diff"
        )
        if path:
            endpoint = f"{endpoint}/{path}"
        params: dict = {}
        if context_lines is not None:
            params["contextLines"] = context_lines
        if whitespace:
            params["whitespace"] = whitespace
        raw_diff = await client.get_raw(endpoint, params=params or None)
        title = f"`{path}`" if path else "all files"
        markdown = f"# Diff for commit `{commit_id[:12]}` ({title})\n\n```diff\n{raw_diff}\n```"
        data = {
            "project_key": project_key,
            "repository_slug": repository_slug,
            "commit_id": commit_id,
            "path": path,
            "diff": raw_diff,
        }
        return render_response(response_format, markdown, data)
