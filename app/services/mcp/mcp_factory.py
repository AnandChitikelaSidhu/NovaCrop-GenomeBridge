from functools import lru_cache

from app.configs.config import Settings, get_settings
from app.services.mcp.mcp_service import MCPService
from app.services.mcp.provider_factory import MCPProviderFactory


class MCPFactory:
    """Creates a fully configured MCPService."""

    @staticmethod
    def create(settings: Settings | None = None) -> MCPService:
        settings = settings or get_settings()

        return MCPService(
            provider_factory=MCPProviderFactory.create_default(
                pubmed_mcp_url=settings.pubmed_mcp_url,
            ),
        )


@lru_cache
def get_mcp_service() -> MCPService:
    return MCPFactory.create()
