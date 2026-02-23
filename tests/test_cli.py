"""CLI behavior tests for server startup options."""

from __future__ import annotations

import sys
import types

import pytest

from mcp_bitbucket_dc import main


def test_cli_defaults_to_localhost_for_http_transport(monkeypatch):
    captured: dict = {}

    async def fake_run_async(**kwargs):
        captured.update(kwargs)

    fake_server = types.SimpleNamespace(mcp=types.SimpleNamespace(run_async=fake_run_async))

    monkeypatch.setitem(sys.modules, "mcp_bitbucket_dc.server", fake_server)
    monkeypatch.setattr(
        sys,
        "argv",
        ["mcp-bitbucket-dc", "--transport", "streamable-http"],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0

    assert captured["transport"] == "streamable-http"
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8000
