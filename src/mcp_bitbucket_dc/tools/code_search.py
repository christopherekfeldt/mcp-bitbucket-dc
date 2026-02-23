"""Code search MCP tool — ported from friend's code to async httpx."""

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from ..client import BitbucketClient
from ..formatting import format_search_results, render_response


def register_code_search_tools(mcp, get_client) -> None:
    """Register code search tools on the MCP server."""

    @mcp.tool(
        tags={"bitbucket", "read"},
        annotations={
            "title": "Code Search",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def bitbucket_code_search(
        ctx: Context,
        query: Annotated[
            str,
            Field(
                description=(
                    "Lucene-style search query. Supports field filters and boolean operators:\n"
                    "- File filters: ext:java, lang:python, path:src/main\n"
                    "- Repository filters: repo:my-repo, project:PROJECT_KEY\n"
                    "- Boolean operators: AND, OR, NOT (uppercase), use () for grouping\n"
                    "- Examples: 'CompanyInfoUpdater', 'function ext:java', "
                    "'config AND (yaml OR yml)', 'className NOT test project:MYPROJ'"
                )
            ),
        ],
        limit: Annotated[
            int,
            Field(description="Number of results per page (1-100)", ge=1, le=100),
        ] = 25,
        start: Annotated[
            int,
            Field(
                description="Starting index for pagination (use nextStart from previous results)"
            ),
        ] = 0,
        response_format: Annotated[
            Literal["markdown", "json"],
            Field(description="Output format: markdown (default) or json"),
        ] = "markdown",
    ) -> str:
        """Search code across all Bitbucket repositories using the search API.

        Uses Bitbucket's built-in code search (powered by Elasticsearch). Searches
        across all repositories the authenticated user has access to. Returns matching
        files with surrounding code context and line numbers.

        Requires the Bitbucket Search feature to be enabled on the Data Center instance.
        """
        client: BitbucketClient = get_client(ctx)
        payload = {
            "query": query,
            "entities": {
                "code": {
                    "start": start,
                    "limit": limit,
                }
            },
        }
        data = await client.post(
            "/rest/search/latest/search",
            json=payload,
            params={"avatarSize": 64},
        )
        code_section = data.get("code", {})
        markdown = format_search_results(
            results=code_section.get("values", []),
            query=query,
            total=code_section.get("count", 0),
            is_last=code_section.get("isLastPage", True),
        )
        return render_response(response_format, markdown, code_section)
