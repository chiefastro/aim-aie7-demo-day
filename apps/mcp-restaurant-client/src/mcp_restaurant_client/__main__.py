#!/usr/bin/env python3
"""MCP Restaurant Client - Main entry point."""

import logging
import sys
from pathlib import Path

import click

from mcp_restaurant_client.server import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host",
    default="localhost",
    help="Host to bind the MCP server to",
)
@click.option(
    "--port",
    default=3000,
    type=int,
    help="Port to bind the MCP server to",
)
@click.option(
    "--a2a-server-url",
    default="http://localhost:4001",
    help="URL of the A2A server to connect to",
)
def cli(host: str, port: int, a2a_server_url: str) -> None:
    """Start the MCP Restaurant Client server."""
    try:
        # The MCP server runs on stdio, so we pass the A2A server URL to main
        main(a2a_server_url=a2a_server_url)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
