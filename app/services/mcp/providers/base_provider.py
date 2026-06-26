from abc import ABC, abstractmethod

from app.services.mcp.models import PubMedSearchRequest, PubMedSearchResult


class BaseMCPProvider(ABC):
    """Strategy interface for MCP-backed external data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    def supports(self, provider_name: str) -> bool:
        return provider_name.lower() == self.name.lower()

    @abstractmethod
    async def search_pubmed(self, request: PubMedSearchRequest) -> PubMedSearchResult:
        raise NotImplementedError
