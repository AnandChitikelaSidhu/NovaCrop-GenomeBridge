from typing import Any

from app.services.mcp.clients.base_client import BaseMCPClient
from app.services.mcp.models import PubMedArticle, PubMedSearchRequest, PubMedSearchResult
from app.services.mcp.providers.base_provider import BaseMCPProvider


class PubMedMCPProvider(BaseMCPProvider):
    """Search and fetch articles from the PubMed MCP server."""

    def __init__(self, client: BaseMCPClient) -> None:
        self.client = client

    @property
    def name(self) -> str:
        return "pubmed"

    async def search_pubmed(self, request: PubMedSearchRequest) -> PubMedSearchResult:
        search_arguments = self._build_search_arguments(request)

        async with self.client.session() as session:
            search_result = await session.call_tool(
                "pubmed_search_articles",
                search_arguments,
            )
            pmids = self._extract_pmids(search_result)
            total_count = self._extract_total_count(search_result)

            if not pmids:
                return PubMedSearchResult(
                    query=request.query,
                    pmids=[],
                    articles=[],
                    total_count=total_count,
                )

            articles_result = await session.call_tool(
                "pubmed_fetch_articles",
                {"pmids": pmids},
            )

        articles = self._parse_articles(articles_result)
        return PubMedSearchResult(
            query=request.query,
            pmids=pmids,
            articles=articles,
            total_count=total_count,
        )

    @staticmethod
    def _build_search_arguments(request: PubMedSearchRequest) -> dict[str, Any]:
        arguments: dict[str, Any] = {
            "query": request.query,
            "maxResults": request.max_results,
            "sort": request.sort,
            "hasAbstract": request.has_abstract,
        }

        if request.date_range:
            arguments["dateRange"] = {
                "minDate": request.date_range.min_date,
                "maxDate": request.date_range.max_date,
                "dateType": request.date_range.date_type,
            }

        return arguments

    @staticmethod
    def _structured_content(result: Any) -> dict[str, Any]:
        structured = getattr(result, "structuredContent", None)
        return structured if isinstance(structured, dict) else {}

    def _extract_pmids(self, result: Any) -> list[str]:
        structured = self._structured_content(result)
        pmids = structured.get("pmids", [])
        return [str(pmid) for pmid in pmids]

    def _extract_total_count(self, result: Any) -> int | None:
        structured = self._structured_content(result)
        total_count = structured.get("totalCount")
        return int(total_count) if total_count is not None else None

    def _parse_articles(self, result: Any) -> list[PubMedArticle]:
        structured = self._structured_content(result)
        raw_articles = structured.get("articles", [])
        articles: list[PubMedArticle] = []

        for raw in raw_articles:
            journal_info = raw.get("journalInfo") or {}
            articles.append(
                PubMedArticle(
                    pmid=str(raw.get("pmid", "")),
                    title=str(raw.get("title", "")),
                    abstract_text=str(raw.get("abstractText", "")),
                    publication_date=self._format_publication_date(journal_info),
                    pubmed_url=str(raw.get("pubmedUrl", "")),
                    doi=raw.get("doi"),
                    pmc_url=raw.get("pmcUrl"),
                    authors=self._format_authors(raw.get("authors")),
                    journal=journal_info.get("title"),
                )
            )

        return articles

    @staticmethod
    def _format_authors(raw_authors: Any) -> list[str]:
        if not raw_authors:
            return []

        formatted: list[str] = []
        for author in raw_authors:
            if isinstance(author, str):
                formatted.append(author)
                continue

            if not isinstance(author, dict):
                formatted.append(str(author))
                continue

            first_name = author.get("firstName") or author.get("foreName") or ""
            last_name = author.get("lastName") or ""
            initials = author.get("initials") or ""

            if first_name and last_name:
                formatted.append(f"{first_name} {last_name}".strip())
            elif last_name and initials:
                formatted.append(f"{last_name} {initials}".strip())
            elif last_name:
                formatted.append(last_name)
            else:
                collective = author.get("collectiveName")
                if collective:
                    formatted.append(str(collective))

        return formatted

    @staticmethod
    def _format_publication_date(journal_info: dict[str, Any]) -> str:
        publication_date = journal_info.get("publicationDate")
        if isinstance(publication_date, dict):
            parts = [
                publication_date.get("year"),
                publication_date.get("month"),
                publication_date.get("day"),
            ]
            return " ".join(str(part) for part in parts if part)
        return str(publication_date or "")
