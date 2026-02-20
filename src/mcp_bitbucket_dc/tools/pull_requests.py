"""Pull request MCP tools."""

from __future__ import annotations

from typing import Annotated, Optional

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import (
    format_pr_activities,
    format_pr_changes,
    format_pull_request_detail,
    format_pull_requests,
)


def register_pull_request_tools(mcp, get_client) -> None:
    """Register pull request tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get Pull Requests", "readOnlyHint": True},
    )
    async def bitbucket_get_pull_requests(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        state: Annotated[
            Optional[str],
            Field(description="PR state filter: OPEN, DECLINED, MERGED, or ALL (default: OPEN)"),
        ] = None,
        direction: Annotated[
            Optional[str],
            Field(description="INCOMING (to this repo) or OUTGOING (from this repo)"),
        ] = None,
        order: Annotated[
            Optional[str],
            Field(description="Order: NEWEST or OLDEST"),
        ] = None,
        filter_text: Annotated[
            Optional[str],
            Field(description="Filter PRs by title text"),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-100)", ge=1, le=100)] = 25,
    ) -> str:
        """List pull requests for a repository.

        Returns pull requests filtered by state, direction, and text. Defaults to
        showing OPEN pull requests ordered by newest first.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if state:
            params["state"] = state
        if direction:
            params["direction"] = direction
        if order:
            params["order"] = order
        if filter_text:
            params["filterText"] = filter_text
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/pull-requests",
            params=params,
            start=start,
            limit=limit,
        )
        return format_pull_requests(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get Pull Request", "readOnlyHint": True},
    )
    async def bitbucket_get_pull_request(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        pull_request_id: Annotated[int, Field(description="The pull request ID number")],
    ) -> str:
        """Get full details of a specific pull request including description and reviewers."""
        client: BitbucketClient = get_client(ctx)
        data = await client.get(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}"
        )
        return format_pull_request_detail(data)

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get PR Comments", "readOnlyHint": True},
    )
    async def bitbucket_get_pull_request_comments(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        pull_request_id: Annotated[int, Field(description="The pull request ID number")],
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-100)", ge=1, le=100)] = 25,
    ) -> str:
        """Get comments and activity for a pull request.

        Returns all activities (comments, approvals, status changes) on the PR,
        including inline code comments with file path and line information.
        """
        client: BitbucketClient = get_client(ctx)
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}/activities",
            start=start,
            limit=limit,
        )
        return format_pr_activities(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get PR Changes", "readOnlyHint": True},
    )
    async def bitbucket_get_pull_request_changes(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        pull_request_id: Annotated[int, Field(description="The pull request ID number")],
        change_scope: Annotated[
            Optional[str],
            Field(description="UNREVIEWED to only show unreviewed changes, or ALL"),
        ] = None,
        with_comments: Annotated[
            Optional[bool],
            Field(description="Include comment counts per file"),
        ] = None,
        start: Annotated[int, Field(description="Pagination start index")] = 0,
        limit: Annotated[int, Field(description="Max results (1-1000)", ge=1, le=1000)] = 25,
    ) -> str:
        """Get the list of files changed in a pull request.

        Shows which files were added, modified, deleted, or renamed in the PR.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if change_scope:
            params["changeScope"] = change_scope
        if with_comments is not None:
            params["withComments"] = str(with_comments).lower()
        data = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}/changes",
            params=params,
            start=start,
            limit=limit,
        )
        return format_pr_changes(
            data.get("values", []),
            total=data.get("size", 0),
            is_last=data.get("isLastPage", True),
        )

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get PR Diff", "readOnlyHint": True},
    )
    async def bitbucket_get_pull_request_diff(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        pull_request_id: Annotated[int, Field(description="The pull request ID number")],
        path: Annotated[str, Field(description="File path to get the diff for")],
        context_lines: Annotated[
            Optional[int],
            Field(description="Number of context lines around changes (default: 10)"),
        ] = None,
        diff_type: Annotated[
            Optional[str],
            Field(description="EFFECTIVE (merge result) or RANGE (commit range)"),
        ] = None,
        whitespace: Annotated[
            Optional[str],
            Field(
                description="Whitespace handling: SHOW, IGNORE_ALL, or IGNORE_TRAILING"
            ),
        ] = None,
    ) -> str:
        """Get the text diff for a specific file in a pull request.

        Returns the unified diff showing additions and deletions for the specified file.
        """
        client: BitbucketClient = get_client(ctx)
        params: dict = {}
        if context_lines is not None:
            params["contextLines"] = context_lines
        if diff_type:
            params["diffType"] = diff_type
        if whitespace:
            params["whitespace"] = whitespace
        raw_diff = await client.get_raw(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}/diff/{path}",
            params=params,
        )
        return f"# Diff: `{path}` (PR #{pull_request_id})\n\n```diff\n{raw_diff}\n```"

    @mcp.tool(
        tags={"bitbucket", "write"},
        annotations={"title": "Post PR Comment", "readOnlyHint": False},
    )
    async def bitbucket_post_pull_request_comment(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        pull_request_id: Annotated[int, Field(description="The pull request ID number")],
        text: Annotated[str, Field(description="The comment text (supports Markdown)")],
        parent_id: Annotated[
            Optional[int],
            Field(description="Parent comment ID to reply to"),
        ] = None,
        file_path: Annotated[
            Optional[str],
            Field(description="File path for inline comment"),
        ] = None,
        line: Annotated[
            Optional[int],
            Field(description="Line number for inline comment"),
        ] = None,
        line_type: Annotated[
            Optional[str],
            Field(description="ADDED, REMOVED, or CONTEXT for inline comments"),
        ] = None,
    ) -> str:
        """Post a comment on a pull request.

        Can post general comments, reply to existing comments, or add inline
        code comments at a specific file and line.
        """
        client: BitbucketClient = get_client(ctx)
        body: dict = {"text": text}
        if parent_id is not None:
            body["parent"] = {"id": parent_id}
        if file_path:
            anchor: dict = {"path": file_path, "fileType": "TO"}
            if line is not None:
                anchor["line"] = line
            if line_type:
                anchor["lineType"] = line_type
            body["anchor"] = anchor
        data = await client.post(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}/comments",
            json=body,
        )
        return f"Comment posted successfully (ID: {data.get('id', 'unknown')})"

    @mcp.tool(
        tags={"bitbucket", "write"},
        annotations={"title": "Create Pull Request", "readOnlyHint": False},
    )
    async def bitbucket_create_pull_request(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        title: Annotated[str, Field(description="PR title")],
        from_ref: Annotated[str, Field(description="Source branch (e.g. 'feature/my-branch')")],
        to_ref: Annotated[str, Field(description="Target branch (e.g. 'main' or 'develop')")],
        description: Annotated[
            Optional[str], Field(description="PR description (supports Markdown)")
        ] = None,
        reviewers: Annotated[
            Optional[list[str]],
            Field(description="List of reviewer usernames to add"),
        ] = None,
    ) -> str:
        """Create a new pull request.

        Creates a PR from `from_ref` branch to `to_ref` branch. Optionally add
        a description and reviewers.
        """
        client: BitbucketClient = get_client(ctx)
        body: dict = {
            "title": title,
            "fromRef": {"id": from_ref},
            "toRef": {"id": to_ref},
        }
        if description:
            body["description"] = description
        if reviewers:
            body["reviewers"] = [{"user": {"name": r}} for r in reviewers]
        data = await client.post(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}/pull-requests",
            json=body,
        )
        pr_id = data.get("id", "unknown")
        return f"Pull request created successfully (ID: #{pr_id})\n\n{format_pull_request_detail(data)}"

    @mcp.tool(
        tags={"bitbucket", "write"},
        annotations={"title": "Update Pull Request", "readOnlyHint": False},
    )
    async def bitbucket_update_pull_request(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        pull_request_id: Annotated[int, Field(description="The pull request ID number")],
        version: Annotated[
            int,
            Field(
                description="Current version of the PR (for optimistic locking — "
                "get from bitbucket_get_pull_request)"
            ),
        ],
        title: Annotated[Optional[str], Field(description="New PR title")] = None,
        description: Annotated[
            Optional[str], Field(description="New PR description")
        ] = None,
        reviewers: Annotated[
            Optional[list[str]],
            Field(description="Full list of reviewer usernames (replaces existing)"),
        ] = None,
    ) -> str:
        """Update a pull request's title, description, or reviewers.

        Requires the current PR `version` number for optimistic locking — fetch it
        first using bitbucket_get_pull_request.
        """
        client: BitbucketClient = get_client(ctx)
        # First get current PR to preserve required fields
        current = await client.get(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}"
        )
        body: dict = {
            "version": version,
            "title": title or current.get("title", ""),
            "fromRef": current.get("fromRef", {}),
            "toRef": current.get("toRef", {}),
        }
        if description is not None:
            body["description"] = description
        if reviewers is not None:
            body["reviewers"] = [{"user": {"name": r}} for r in reviewers]
        elif current.get("reviewers"):
            body["reviewers"] = current["reviewers"]
        data = await client.put(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/pull-requests/{pull_request_id}",
            json=body,
        )
        return f"Pull request updated successfully.\n\n{format_pull_request_detail(data)}"

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={"title": "Get Required Reviewers", "readOnlyHint": True},
    )
    async def bitbucket_get_required_reviewers(
        ctx: Context,
        project_key: Annotated[str, Field(description="The project key")],
        repository_slug: Annotated[str, Field(description="The repository slug")],
        source_ref: Annotated[str, Field(description="Source branch ref ID")],
        target_ref: Annotated[str, Field(description="Target branch ref ID")],
    ) -> str:
        """Get required reviewers for a potential pull request between two branches.

        Use this before creating a PR to discover mandatory reviewers configured
        via merge checks or default reviewer rules.
        """
        client: BitbucketClient = get_client(ctx)
        data = await client.get(
            f"/rest/api/latest/projects/{project_key}/repos/{repository_slug}"
            f"/conditions",
            params={"sourceRefId": source_ref, "targetRefId": target_ref},
        )
        # Parse the conditions response
        conditions = data if isinstance(data, list) else data.get("values", [data])
        lines = ["# Required Reviewers\n"]
        for cond in conditions:
            reviewers_list = cond.get("reviewers", [])
            for r in reviewers_list:
                lines.append(f"- **{r.get('displayName', r.get('name', 'unknown'))}** (`{r.get('name', '')}`)")
            required_approvals = cond.get("requiredApprovals", 0)
            if required_approvals:
                lines.append(f"\n*Required approvals: {required_approvals}*")
        if len(lines) == 1:
            lines.append("No required reviewers configured for this branch combination.")
        return "\n".join(lines)
