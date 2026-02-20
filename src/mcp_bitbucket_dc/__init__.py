"""MCP Bitbucket Data Center — entry point for uvx / CLI."""

from __future__ import annotations

import asyncio
import logging
import sys


def main() -> None:
    """Run the Bitbucket DC MCP server (stdio transport by default)."""
    import click

    @click.command()
    @click.option(
        "--transport",
        type=click.Choice(["stdio", "sse", "streamable-http"]),
        default="stdio",
        help="MCP transport protocol",
    )
    @click.option("--host", default="0.0.0.0", help="Host to bind (SSE/HTTP only)")
    @click.option("--port", default=8000, type=int, help="Port to bind (SSE/HTTP only)")
    @click.option("--log-level", default="WARNING", help="Logging level")
    def run(transport: str, host: str, port: int, log_level: str) -> None:
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.WARNING),
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            stream=sys.stderr,
        )

        from .server import mcp

        run_kwargs: dict = {"transport": transport}
        if transport in ("sse", "streamable-http"):
            run_kwargs["host"] = host
            run_kwargs["port"] = port

        asyncio.run(mcp.run_async(**run_kwargs))

    run()


if __name__ == "__main__":
    main()
