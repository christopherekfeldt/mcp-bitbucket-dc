"""Configuration for Bitbucket Data Center MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BitbucketConfig:
    """Bitbucket Data Center connection configuration.

    Reads from environment variables:
        BITBUCKET_HOST: Domain + optional port (e.g. "git.company.se" or "git.company.se:7990")
        BITBUCKET_URL:  Full base URL alternative (e.g. "https://git.company.se")
        BITBUCKET_API_TOKEN: Personal Access Token for authentication
    """

    base_url: str
    api_token: str

    @classmethod
    def from_env(cls) -> BitbucketConfig:
        """Create configuration from environment variables."""
        token = os.environ.get("BITBUCKET_API_TOKEN", "")
        if not token:
            raise ValueError(
                "BITBUCKET_API_TOKEN environment variable is required. "
                "Generate a Personal Access Token in Bitbucket: "
                "Manage Account → HTTP access tokens → Create token"
            )

        # Support BITBUCKET_URL (full URL) or BITBUCKET_HOST (domain only)
        base_url = os.environ.get("BITBUCKET_URL", "")
        if not base_url:
            host = os.environ.get("BITBUCKET_HOST", "")
            if not host:
                raise ValueError(
                    "Either BITBUCKET_URL or BITBUCKET_HOST environment variable is required. "
                    "Example: BITBUCKET_HOST=git.company.se"
                )
            # Strip protocol if accidentally included
            host = host.removeprefix("https://").removeprefix("http://")
            base_url = f"https://{host}"

        # Normalize: remove trailing slash
        base_url = base_url.rstrip("/")

        return cls(base_url=base_url, api_token=token)

    @property
    def rest_api_url(self) -> str:
        """Base URL for Bitbucket REST API endpoints."""
        return f"{self.base_url}/rest/api/latest"

    @property
    def search_api_url(self) -> str:
        """Base URL for Bitbucket Search API endpoints."""
        return f"{self.base_url}/rest/search/latest"
