"""Tests for BitbucketConfig."""

from __future__ import annotations

import pytest

from mcp_bitbucket_dc.config import BitbucketConfig


class TestBitbucketConfig:
    def test_from_env_with_host(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_HOST", "git.example.com")
        monkeypatch.setenv("BITBUCKET_API_TOKEN", "my-token")
        monkeypatch.delenv("BITBUCKET_URL", raising=False)

        config = BitbucketConfig.from_env()
        assert config.base_url == "https://git.example.com"
        assert config.api_token == "my-token"
        assert config.rest_api_url == "https://git.example.com/rest/api/latest"
        assert config.search_api_url == "https://git.example.com/rest/search/latest"

    def test_from_env_with_url(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_URL", "https://git.example.com")
        monkeypatch.setenv("BITBUCKET_API_TOKEN", "my-token")
        monkeypatch.delenv("BITBUCKET_HOST", raising=False)

        config = BitbucketConfig.from_env()
        assert config.base_url == "https://git.example.com"

    def test_from_env_strips_trailing_slash(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_URL", "https://git.example.com/")
        monkeypatch.setenv("BITBUCKET_API_TOKEN", "my-token")
        monkeypatch.delenv("BITBUCKET_HOST", raising=False)

        config = BitbucketConfig.from_env()
        assert config.base_url == "https://git.example.com"

    def test_from_env_strips_protocol_from_host(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_HOST", "https://git.example.com")
        monkeypatch.setenv("BITBUCKET_API_TOKEN", "my-token")
        monkeypatch.delenv("BITBUCKET_URL", raising=False)

        config = BitbucketConfig.from_env()
        assert config.base_url == "https://git.example.com"

    def test_from_env_missing_token(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_HOST", "git.example.com")
        monkeypatch.delenv("BITBUCKET_API_TOKEN", raising=False)

        with pytest.raises(ValueError, match="BITBUCKET_API_TOKEN"):
            BitbucketConfig.from_env()

    def test_from_env_missing_host_and_url(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_API_TOKEN", "my-token")
        monkeypatch.delenv("BITBUCKET_HOST", raising=False)
        monkeypatch.delenv("BITBUCKET_URL", raising=False)

        with pytest.raises(ValueError, match="BITBUCKET_URL or BITBUCKET_HOST"):
            BitbucketConfig.from_env()
