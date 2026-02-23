"""Live smoke tests against a real/staging Bitbucket DC instance.

These tests are skipped by default and only run when RUN_LIVE_SMOKE=1.
They use existing BITBUCKET_HOST/BITBUCKET_URL and BITBUCKET_API_TOKEN env vars.
"""

import os

import pytest

from mcp_bitbucket_dc.client import BitbucketClient
from mcp_bitbucket_dc.config import BitbucketConfig

pytestmark = pytest.mark.integration


def _live_enabled() -> bool:
    return os.getenv("RUN_LIVE_SMOKE", "0") == "1"


@pytest.mark.asyncio
async def test_live_smoke_projects_list():
    if not _live_enabled():
        pytest.skip("Set RUN_LIVE_SMOKE=1 to run live smoke tests")

    config = BitbucketConfig.from_env()
    client = BitbucketClient(config)
    try:
        data = await client.get_paged("/rest/api/latest/projects", limit=5)
        assert isinstance(data, dict)
        assert "values" in data
        assert isinstance(data["values"], list)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_live_smoke_repos_and_commits():
    if not _live_enabled():
        pytest.skip("Set RUN_LIVE_SMOKE=1 to run live smoke tests")

    config = BitbucketConfig.from_env()
    client = BitbucketClient(config)
    try:
        projects = await client.get_paged("/rest/api/latest/projects", limit=1)
        if not projects.get("values"):
            pytest.skip("No visible projects for the configured token")

        project_key = projects["values"][0]["key"]

        repos = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos",
            limit=1,
        )
        if not repos.get("values"):
            pytest.skip(f"No visible repositories in project {project_key}")

        repo_slug = repos["values"][0]["slug"]

        commits = await client.get_paged(
            f"/rest/api/latest/projects/{project_key}/repos/{repo_slug}/commits",
            limit=1,
        )
        assert isinstance(commits, dict)
        assert "values" in commits
        assert isinstance(commits["values"], list)
    finally:
        await client.close()
