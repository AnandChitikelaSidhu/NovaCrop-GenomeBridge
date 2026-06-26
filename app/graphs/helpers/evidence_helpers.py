from langchain_openai import ChatOpenAI

from app.configs.config import Settings, get_settings
from app.graphs.schemas.validation_assessment import ValidationAssessment
from app.graphs.state import (
    Agreement,
    Disagreement,
    ExternalSource,
    GenomeBridgeState,
    InternalSource,
    ValidationResult,
)


def build_llm(settings: Settings | None = None) -> ChatOpenAI:
    settings = settings or get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.chat_model,
        temperature=0,
    )


def should_validate_sync(state: GenomeBridgeState) -> bool:
    return (
        state.get("route") == "both"
        and state.get("internal_status") == "found"
        and state.get("external_status") == "found"
    )


def format_internal_evidence(
    state: GenomeBridgeState,
    *,
    include_answer: bool = True,
) -> str:
    status = state.get("internal_status", "empty")
    if status == "skipped":
        return "Internal knowledge base was not queried for this question."

    sources: list[InternalSource] = state.get("internal_sources") or []
    if status == "empty" or not sources:
        return "No relevant excerpts were found in NovaCrop's internal knowledge base."

    blocks: list[str] = []
    if include_answer:
        answer = state.get("internal_answer") or ""
        if answer.strip():
            blocks.append(f"Internal answer draft:\n{answer}")

    for index, source in enumerate(sources, start=1):
        blocks.append(
            f"[Internal {index}] Source: {source.source} ({source.file_type})\n"
            f"{source.excerpt}"
        )

    return "\n\n".join(blocks)


def format_external_evidence(state: GenomeBridgeState) -> str:
    status = state.get("external_status", "empty")
    if status == "skipped":
        return "External PubMed literature was not queried for this question."

    sources: list[ExternalSource] = state.get("external_sources") or []
    if status == "empty" or not sources:
        summary = state.get("external_summary") or "No PubMed articles matched the query."
        return summary

    blocks = [f"External retrieval summary:\n{state.get('external_summary') or ''}"]
    for index, source in enumerate(sources, start=1):
        authors = ", ".join(source.authors) if source.authors else "Unknown"
        blocks.append(
            f"[External {index}] PMID: {source.pmid} — {source.title}\n"
            f"Published: {source.publication_date} | Journal: {source.journal or 'n/a'}\n"
            f"Authors: {authors}\n"
            f"Abstract excerpt:\n{source.excerpt}"
        )

    return "\n\n".join(blocks)


def format_validation_result(validation: ValidationResult | None) -> str:
    if validation is None:
        return "No cross-source validation was performed."

    lines = [f"Validation confidence: {validation.confidence}"]

    if validation.agreements:
        lines.append("Agreements:")
        for item in validation.agreements:
            lines.append(
                f"- {item.claim} "
                f"(internal: {item.internal_source}, external PMID: {item.external_source})"
            )

    if validation.disagreements:
        lines.append("Disagreements:")
        for item in validation.disagreements:
            lines.append(
                f"- Internal ({item.internal_source}): {item.claim_internal} | "
                f"External (PMID {item.external_source}): {item.claim_external}"
            )

    if validation.internal_only:
        lines.append("Internal-only findings:")
        for item in validation.internal_only:
            lines.append(f"- {item}")

    if validation.external_only:
        lines.append("External-only findings:")
        for item in validation.external_only:
            lines.append(f"- {item}")

    return "\n".join(lines)


def to_validation_result(assessment: ValidationAssessment) -> ValidationResult:
    return ValidationResult(
        agreements=[
            Agreement(
                claim=item.claim,
                internal_source=item.internal_source,
                external_source=item.external_source,
            )
            for item in assessment.agreements
        ],
        disagreements=[
            Disagreement(
                claim_internal=item.claim_internal,
                internal_source=item.internal_source,
                claim_external=item.claim_external,
                external_source=item.external_source,
            )
            for item in assessment.disagreements
        ],
        internal_only=list(assessment.internal_only),
        external_only=list(assessment.external_only),
        confidence=assessment.confidence,
    )


def has_usable_evidence(state: GenomeBridgeState) -> bool:
    route = state.get("route", "internal")
    internal_status = state.get("internal_status", "empty")
    external_status = state.get("external_status", "empty")

    if route == "internal":
        return internal_status == "found"
    if route == "external":
        return external_status == "found"
    return internal_status == "found" or external_status == "found"
