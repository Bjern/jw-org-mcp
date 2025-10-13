"""JW.Org MCP Tool - Model Context Protocol server for verified jw.org content access."""

import asyncio

from mcp.server.stdio import stdio_server

from .server import app, cleanup


def main() -> None:
    """Main entry point for the MCP server."""
    asyncio.run(async_main())


async def async_main() -> None:
    """Async main function."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    finally:
        await cleanup()
