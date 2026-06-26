import asyncio

from app.services.mcp.mcp_factory import MCPFactory
from app.services.mcp.models import PubMedDateRange, PubMedSearchRequest


async def main() -> None:
    mcp = MCPFactory.create()

    result = await mcp.search_pubmed(
        PubMedSearchRequest(
            query="drought tolerance rice",
            max_results=5,
            sort="pub_date",
            has_abstract=True,
            date_range=PubMedDateRange(
                min_date="2023",
                max_date="2026",
                date_type="pdat",
            ),
        )
    )

    print(f"Found {len(result.pmids)} PMIDs: {result.pmids}\n")

    for article in result.articles:
        print(f"Title      : {article.title}")
        print(f"Abstract   : {article.abstract_text[:200]}...")
        print(f"Published  : {article.publication_date}")
        print(f"PubMed URL : {article.pubmed_url}")
        print(f"PMC URL    : {article.pmc_url or 'N/A'}")
        print(f"DOI        : {article.doi or 'N/A'}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
