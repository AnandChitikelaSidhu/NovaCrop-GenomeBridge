from app.graphs.state import EvidenceStatus, ExternalSource, GenomeBridgeState, InternalSource
from app.services.mcp.mcp_factory import MCPFactory
from app.services.mcp.models import PubMedArticle, PubMedSearchRequest
from app.services.rag.rag_factory import RAGFactory


def _internal_query(state: GenomeBridgeState) -> str:
    return (state.get("internal_query") or state.get("question") or "").strip()


def _external_query(state: GenomeBridgeState) -> str:
    return (state.get("external_query") or state.get("question") or "").strip()


def _to_internal_sources(chunks) -> list[InternalSource]:
    return [
        InternalSource(
            source=chunk.source,
            file_type=chunk.file_type,
            excerpt=chunk.excerpt,
            score=chunk.score,
        )
        for chunk in chunks
    ]


def _to_external_sources(articles: list[PubMedArticle]) -> list[ExternalSource]:
    return [
        ExternalSource(
            pmid=article.pmid,
            title=article.title,
            pubmed_url=article.pubmed_url,
            publication_date=article.publication_date,
            excerpt=article.abstract_text,
            doi=article.doi,
            pmc_url=article.pmc_url,
            authors=list(article.authors),
            journal=article.journal,
        )
        for article in articles
    ]


def _internal_status(has_context: bool) -> EvidenceStatus:
    return "found" if has_context else "empty"


def _external_status(articles: list[PubMedArticle]) -> EvidenceStatus:
    return "found" if articles else "empty"


def _external_summary(query: str, articles: list[PubMedArticle]) -> str:
    if not articles:
        return f"No PubMed articles matched the query: {query!r}."
    count = len(articles)
    noun = "article" if count == 1 else "articles"
    return f"PubMed returned {count} {noun} for: {query!r}."


def run_internal_fetch(state: GenomeBridgeState, *, top_k: int = 5) -> dict:
    query = _internal_query(state)
    rag = RAGFactory.create()
    result = rag.query_with_evidence(query, top_k=top_k)

    return {
        "internal_answer": result.answer,
        "internal_sources": _to_internal_sources(result.chunks),
        "internal_status": _internal_status(result.has_context),
    }


async def run_external_fetch(state: GenomeBridgeState) -> dict:
    query = _external_query(state)
    if not query:
        return {
            "external_summary": "No external query was provided.",
            "external_sources": [],
            "external_status": "empty",
        }

    request = PubMedSearchRequest(
        query=query,
        max_results=state.get("external_max_results", 5),
        date_range=state.get("external_date_range"),
    )

    mcp = MCPFactory.create()
    result = await mcp.search_pubmed(request)
    articles = result.articles

    return {
        "external_summary": _external_summary(query, articles),
        "external_sources": _to_external_sources(articles),
        "external_status": _external_status(articles),
    }


def skipped_external_fields() -> dict:
    return {
        "external_summary": None,
        "external_sources": [],
        "external_status": "skipped",
    }


def skipped_internal_fields() -> dict:
    return {
        "internal_answer": None,
        "internal_sources": [],
        "internal_status": "skipped",
    }
