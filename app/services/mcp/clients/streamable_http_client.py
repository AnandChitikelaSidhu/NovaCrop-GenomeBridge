from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from app.services.mcp.clients.base_client import BaseMCPClient


class StreamableHttpMCPClient(BaseMCPClient):
    """MCP client over Streamable HTTP transport."""

    def __init__(self, server_url: str) -> None:
        self.server_url = server_url

    @asynccontextmanager
    async def session(self) -> AsyncIterator[ClientSession]:
        async with streamablehttp_client(self.server_url) as (read, write, _):
            async with ClientSession(read, write) as client_session:
                await client_session.initialize()
                yield client_session
