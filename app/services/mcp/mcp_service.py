from app.services.mcp.models import PubMedSearchRequest, PubMedSearchResult
from app.services.mcp.provider_factory import MCPProviderFactory


class MCPService:
    """Orchestrates external literature queries via MCP providers."""

    def __init__(self, provider_factory: MCPProviderFactory) -> None:
        self.provider_factory = provider_factory

    async def search_pubmed(self, request: PubMedSearchRequest) -> PubMedSearchResult:
        provider = self.provider_factory.get_provider("pubmed")
        return await provider.search_pubmed(request)
