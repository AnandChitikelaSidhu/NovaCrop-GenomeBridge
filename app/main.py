from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.graphs.api_models import (
    GenomeBridgeQueryRequest,
    GenomeBridgeQueryResponse,
    state_to_response,
)
from app.graphs.graph_factory import get_genome_bridge_graph
from app.services.mcp.mcp_factory import get_mcp_service
from app.services.mcp.mcp_service import MCPService
from app.services.mcp.models import PubMedDateRange, PubMedSearchRequest
from app.services.rag.rag_factory import get_rag_service
from app.services.rag.rag_service import RAGService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_DATA_DIR = PROJECT_ROOT / "data" / "pdf"
TXT_DATA_DIR = PROJECT_ROOT / "data" / "txt"

app = FastAPI(title="NovaCrop-GenomeBridge", version="0.1.0")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str


class IngestResponse(BaseModel):
    chunks_by_directory: dict[str, int]


class PubMedDateRangeRequest(BaseModel):
    min_date: str = Field(..., alias="minDate")
    max_date: str = Field(..., alias="maxDate")
    date_type: str = Field(default="pdat", alias="dateType")

    model_config = {"populate_by_name": True}


class PubMedSearchRequestBody(BaseModel):
    query: str = Field(..., min_length=1)
    max_results: int = Field(default=5, ge=1, le=100, alias="maxResults")
    sort: str = Field(default="pub_date")
    has_abstract: bool = Field(default=True, alias="hasAbstract")
    date_range: PubMedDateRangeRequest | None = Field(default=None, alias="dateRange")

    model_config = {"populate_by_name": True}


class PubMedArticleResponse(BaseModel):
    pmid: str
    title: str
    abstract_text: str
    publication_date: str
    pubmed_url: str
    doi: str | None = None
    pmc_url: str | None = None
    authors: list[str] = []
    journal: str | None = None


class PubMedSearchResponse(BaseModel):
    query: str
    pmids: list[str]
    total_count: int | None = None
    articles: list[PubMedArticleResponse]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest_documents(rag: RAGService = Depends(get_rag_service)) -> IngestResponse:
    result = rag.ingest_data_directories(PDF_DATA_DIR, TXT_DATA_DIR)
    return IngestResponse(chunks_by_directory=result)


@app.post("/ingest/{filename}")
def ingest_file(
    filename: str,
    rag: RAGService = Depends(get_rag_service),
) -> dict[str, int | str]:
    pdf_path = PDF_DATA_DIR / filename
    txt_path = TXT_DATA_DIR / filename

    if pdf_path.exists():
        file_path = pdf_path
    elif txt_path.exists():
        file_path = txt_path
    else:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    chunks = rag.ingest_file(file_path)
    return {"filename": filename, "chunks_ingested": chunks}


@app.post("/query", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    rag: RAGService = Depends(get_rag_service),
) -> QueryResponse:
    answer = rag.query(request.question, top_k=request.top_k)
    return QueryResponse(answer=answer)


@app.post("/genomebridge/query", response_model=GenomeBridgeQueryResponse)
async def genomebridge_query(
    request: GenomeBridgeQueryRequest,
) -> GenomeBridgeQueryResponse:
    graph = get_genome_bridge_graph()
    result = await graph.ainvoke({"question": request.question})
    return state_to_response(result)


@app.post("/mcp/pubmed/search", response_model=PubMedSearchResponse)
async def search_pubmed(
    request: PubMedSearchRequestBody,
    mcp: MCPService = Depends(get_mcp_service),
) -> PubMedSearchResponse:
    date_range = None
    if request.date_range:
        date_range = PubMedDateRange(
            min_date=request.date_range.min_date,
            max_date=request.date_range.max_date,
            date_type=request.date_range.date_type,
        )

    result = await mcp.search_pubmed(
        PubMedSearchRequest(
            query=request.query,
            max_results=request.max_results,
            sort=request.sort,
            has_abstract=request.has_abstract,
            date_range=date_range,
        )
    )

    return PubMedSearchResponse(
        query=result.query,
        pmids=result.pmids,
        total_count=result.total_count,
        articles=[
            PubMedArticleResponse(
                pmid=article.pmid,
                title=article.title,
                abstract_text=article.abstract_text,
                publication_date=article.publication_date,
                pubmed_url=article.pubmed_url,
                doi=article.doi,
                pmc_url=article.pmc_url,
                authors=article.authors,
                journal=article.journal,
            )
            for article in result.articles
        ],
    )


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
