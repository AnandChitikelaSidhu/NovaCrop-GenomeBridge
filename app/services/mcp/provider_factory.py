from collections.abc import Iterable

from app.services.mcp.providers.base_provider import BaseMCPProvider


class MCPProviderFactory:
    """Factory that selects the correct MCP provider strategy."""

    def __init__(self, providers: Iterable[BaseMCPProvider]) -> None:
        self._providers = list(providers)

    @classmethod
    def create_default(cls, pubmed_mcp_url: str) -> "MCPProviderFactory":
        from app.services.mcp.clients.streamable_http_client import StreamableHttpMCPClient
        from app.services.mcp.providers.pubmed_provider import PubMedMCPProvider

        pubmed_client = StreamableHttpMCPClient(server_url=pubmed_mcp_url)

        return cls(
            providers=[
                PubMedMCPProvider(client=pubmed_client),
            ]
        )

    def get_provider(self, provider_name: str) -> BaseMCPProvider:
        for provider in self._providers:
            if provider.supports(provider_name):
                return provider

        supported = ", ".join(sorted(provider.name for provider in self._providers))
        raise ValueError(
            f"Unsupported MCP provider '{provider_name}'. Supported providers: {supported}"
        )
