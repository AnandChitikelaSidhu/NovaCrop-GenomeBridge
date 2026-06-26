from dataclasses import dataclass, field
from typing import Literal, TypedDict

from app.services.mcp.models import PubMedDateRange

Route = Literal["internal", "external", "both"]
EvidenceStatus = Literal["found", "empty", "skipped"]
ValidationConfidence = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class InternalSource:
    source: str
    file_type: str
    excerpt: str
    score: float | None = None


@dataclass(frozen=True)
class ExternalSource:
    pmid: str
    title: str
    pubmed_url: str
    publication_date: str
    excerpt: str
    doi: str | None = None
    pmc_url: str | None = None
    authors: list[str] = field(default_factory=list)
    journal: str | None = None


@dataclass(frozen=True)
class Agreement:
    claim: str
    internal_source: str
    external_source: str


@dataclass(frozen=True)
class Disagreement:
    claim_internal: str
    internal_source: str
    claim_external: str
    external_source: str


@dataclass
class ValidationResult:
    agreements: list[Agreement] = field(default_factory=list)
    disagreements: list[Disagreement] = field(default_factory=list)
    internal_only: list[str] = field(default_factory=list)
    external_only: list[str] = field(default_factory=list)
    confidence: ValidationConfidence = "medium"


@dataclass
class PlannedQueries:
    internal_query: str | None = None
    external_query: str | None = None
    external_date_range: PubMedDateRange | None = None
    external_max_results: int = 5


class GenomeBridgeState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.

    Each node reads what it needs and returns a partial update dict.
    Fields are optional in the TypedDict because nodes set them incrementally.

    Example final state (route="both"):

        {
            "question": "What have we and others published on drought markers since 2023?",
            "route": "both",
            "route_reason": "Question compares NovaCrop internal work with published literature.",
            "internal_query": "drought tolerance SNP markers rice",
            "external_query": "drought tolerance markers rice",
            "external_date_range": PubMedDateRange(
                min_date="2023",
                max_date="2026",
                date_type="pdat",
            ),
            "external_max_results": 5,
            "internal_answer": "NovaCrop identified 12 SNP markers associated with drought tolerance...",
            "external_summary": "PubMed returned 5 articles on drought tolerance markers in rice.",
            "internal_sources": [
                InternalSource(
                    source="data/txt/Drought_Tolerance_Rice.txt",
                    file_type="txt",
                    excerpt="This study identified twelve significant SNP markers...",
                    score=0.89,
                ),
            ],
            "external_sources": [
                ExternalSource(
                    pmid="41935025",
                    title="PgWRKY44-mediated modulation of SA/JA pathways...",
                    pubmed_url="https://pubmed.ncbi.nlm.nih.gov/41935025/",
                    publication_date="2026 Dec 31",
                    excerpt="The complex network of plant defense mechanisms...",
                    doi="10.1080/15592324.2026.2650899",
                    pmc_url="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13051619/",
                    authors=["Baisista Saha", "Sushmita Saha"],
                    journal="Plant signaling & behavior",
                ),
            ],
            "internal_status": "found",
            "external_status": "found",
            "in_sync": True,
            "validation": ValidationResult(
                agreements=[
                    Agreement(
                        claim="SNP markers are associated with drought tolerance in rice.",
                        internal_source="data/txt/Drought_Tolerance_Rice.txt",
                        external_source="41935025",
                    ),
                ],
                disagreements=[],
                internal_only=["18% yield improvement using marker-assisted selection."],
                external_only=["PgWRKY44 pathway modulation in pearl millet and rice."],
                confidence="medium",
            ),
            "answer": (
                "NovaCrop's internal knowledge base reports 12 SNP markers linked to drought "
                "tolerance in rice (Source: data/txt/Drought_Tolerance_Rice.txt). PubMed "
                "literature from 2023–2026 reports related drought-tolerance research in "
                "rice (PubMed: 41935025). The sources align on SNP-marker-based drought "
                "research, though specific yield figures appear only in internal documents."
            ),
        }

    route="internal"  → external_status="skipped", external_sources=[], in_sync=None
    route="external"  → internal_status="skipped", internal_sources=[], in_sync=None
    either side empty → in_sync=None, validation=None (no sync check)
    """

    # Input
    question: str

    # Routing
    route: Route
    route_reason: str

    # Query planning
    planned_queries: PlannedQueries
    internal_query: str | None
    external_query: str | None
    external_date_range: PubMedDateRange | None
    external_max_results: int

    # Retrieval results
    internal_answer: str | None
    external_summary: str | None
    internal_sources: list[InternalSource]
    external_sources: list[ExternalSource]
    internal_status: EvidenceStatus
    external_status: EvidenceStatus

    # Validation (route=both and both sides found)
    in_sync: bool | None
    validation: ValidationResult | None

    # Final output
    answer: str



