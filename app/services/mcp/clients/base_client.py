from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession


class BaseMCPClient(ABC):
    """Strategy interface for MCP transport clients."""

    @asynccontextmanager
    @abstractmethod
    async def session(self) -> AsyncIterator[ClientSession]:
        raise NotImplementedError

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with self.session() as client_session:
            return await client_session.call_tool(tool_name, arguments)
