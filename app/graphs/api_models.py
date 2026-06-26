from pydantic import BaseModel, Field

from app.graphs.state import (
    EvidenceStatus,
    ExternalSource,
    GenomeBridgeState,
    InternalSource,
    Route,
    ValidationConfidence,
    ValidationResult,
)


class GenomeBridgeQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class InternalSourceResponse(BaseModel):
    source: str
    file_type: str
    excerpt: str
    score: float | None = None


class ExternalSourceResponse(BaseModel):
    pmid: str
    title: str
    pubmed_url: str
    publication_date: str
    excerpt: str
    doi: str | None = None
    pmc_url: str | None = None
    authors: list[str] = []
    journal: str | None = None


class AgreementResponse(BaseModel):
    claim: str
    internal_source: str
    external_source: str


class DisagreementResponse(BaseModel):
    claim_internal: str
    internal_source: str
    claim_external: str
    external_source: str


class ValidationResponse(BaseModel):
    agreements: list[AgreementResponse] = []
    disagreements: list[DisagreementResponse] = []
    internal_only: list[str] = []
    external_only: list[str] = []
    confidence: ValidationConfidence = "medium"


class GenomeBridgeQueryResponse(BaseModel):
    answer: str
    route: Route
    route_reason: str
    internal_query: str | None = None
    external_query: str | None = None
    internal_answer: str | None = None
    external_summary: str | None = None
    internal_status: EvidenceStatus
    external_status: EvidenceStatus
    internal_sources: list[InternalSourceResponse] = []
    external_sources: list[ExternalSourceResponse] = []
    in_sync: bool | None = None
    validation: ValidationResponse | None = None


def _internal_source(source: InternalSource) -> InternalSourceResponse:
    return InternalSourceResponse(
        source=source.source,
        file_type=source.file_type,
        excerpt=source.excerpt,
        score=source.score,
    )


def _external_source(source: ExternalSource) -> ExternalSourceResponse:
    return ExternalSourceResponse(
        pmid=source.pmid,
        title=source.title,
        pubmed_url=source.pubmed_url,
        publication_date=source.publication_date,
        excerpt=source.excerpt,
        doi=source.doi,
        pmc_url=source.pmc_url,
        authors=list(source.authors),
        journal=source.journal,
    )


def _validation_result(validation: ValidationResult) -> ValidationResponse:
    return ValidationResponse(
        agreements=[
            AgreementResponse(
                claim=item.claim,
                internal_source=item.internal_source,
                external_source=item.external_source,
            )
            for item in validation.agreements
        ],
        disagreements=[
            DisagreementResponse(
                claim_internal=item.claim_internal,
                internal_source=item.internal_source,
                claim_external=item.claim_external,
                external_source=item.external_source,
            )
            for item in validation.disagreements
        ],
        internal_only=list(validation.internal_only),
        external_only=list(validation.external_only),
        confidence=validation.confidence,
    )


def state_to_response(state: GenomeBridgeState) -> GenomeBridgeQueryResponse:
    validation = state.get("validation")
    return GenomeBridgeQueryResponse(
        answer=state.get("answer", ""),
        route=state.get("route", "internal"),
        route_reason=state.get("route_reason", ""),
        internal_query=state.get("internal_query"),
        external_query=state.get("external_query"),
        internal_answer=state.get("internal_answer"),
        external_summary=state.get("external_summary"),
        internal_status=state.get("internal_status", "empty"),
        external_status=state.get("external_status", "empty"),
        internal_sources=[
            _internal_source(source) for source in (state.get("internal_sources") or [])
        ],
        external_sources=[
            _external_source(source) for source in (state.get("external_sources") or [])
        ],
        in_sync=state.get("in_sync"),
        validation=_validation_result(validation) if validation else None,
    )
