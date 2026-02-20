"""Async HTTP client for Bitbucket Data Center REST API."""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from .config import BitbucketConfig

logger = logging.getLogger(__name__)


class BitbucketClientError(Exception):
    """Raised when a Bitbucket API request fails."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Bitbucket API error ({status_code}): {message}")


class BitbucketClient:
    """Async HTTP client for Bitbucket Data Center.

    Wraps httpx.AsyncClient with PAT authentication and standard error handling.
    """

    def __init__(self, config: BitbucketConfig) -> None:
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=10.0),
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    # ── Core HTTP methods ───────────────────────────────────────────────────

    async def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a GET request to the Bitbucket API."""
        response = await self._client.get(path, params=params)
        return self._handle_response(response)

    async def post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a POST request to the Bitbucket API."""
        response = await self._client.post(path, json=json, params=params)
        return self._handle_response(response)

    async def put(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a PUT request to the Bitbucket API."""
        response = await self._client.put(path, json=json)
        return self._handle_response(response)

    async def delete(self, path: str) -> dict[str, Any]:
        """Make a DELETE request to the Bitbucket API."""
        response = await self._client.delete(path)
        return self._handle_response(response)

    async def get_raw(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> str:
        """Make a GET request and return raw text (for file content)."""
        response = await self._client.get(path, params=params)
        self._check_errors(response)
        return response.text

    # ── Convenience: REST API paths ─────────────────────────────────────────

    def _repo_path(self, project_key: str, repo_slug: str) -> str:
        """Build the REST API path prefix for a repository."""
        return f"/rest/api/latest/projects/{project_key}/repos/{repo_slug}"

    async def get_paged(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Make a GET request with pagination parameters."""
        p = dict(params or {})
        p["start"] = start
        p["limit"] = limit
        return await self.get(path, params=p)

    # ── Response handling ───────────────────────────────────────────────────

    def _check_errors(self, response: httpx.Response) -> None:
        """Raise descriptive errors for non-2xx responses."""
        if response.is_success:
            return

        status = response.status_code
        try:
            body = response.json()
            errors = body.get("errors", [])
            if errors:
                messages = "; ".join(e.get("message", str(e)) for e in errors)
            else:
                messages = body.get("message", response.text[:500])
        except Exception:
            messages = response.text[:500]

        if status == 401:
            raise BitbucketClientError(
                status, "Authentication failed — check your Personal Access Token"
            )
        if status == 403:
            raise BitbucketClientError(
                status, f"Permission denied: {messages}"
            )
        if status == 404:
            raise BitbucketClientError(status, f"Not found: {messages}")

        raise BitbucketClientError(status, messages)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Check for errors and parse JSON response."""
        self._check_errors(response)
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()
