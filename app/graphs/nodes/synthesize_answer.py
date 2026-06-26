from app.graphs.helpers.evidence_helpers import (
    build_llm,
    format_external_evidence,
    format_internal_evidence,
    format_validation_result,
    has_usable_evidence,
)
from app.graphs.prompts.synthesize_answer import SYNTHESIZE_ANSWER_PROMPT
from app.graphs.state import GenomeBridgeState


def _empty_answer(state: GenomeBridgeState) -> str:
    route = state.get("route", "internal")
    question = state.get("question", "").strip()

    if route == "internal":
        return (
            f"Nothing in NovaCrop's internal knowledge base addresses: {question}"
            if question
            else "Nothing in NovaCrop's internal knowledge base addresses this question."
        )

    if route == "external":
        summary = state.get("external_summary")
        if summary:
            return summary
        return (
            f"No PubMed literature was found for: {question}"
            if question
            else "No PubMed literature was found for this question."
        )

    internal_empty = state.get("internal_status") != "found"
    external_empty = state.get("external_status") != "found"
    if internal_empty and external_empty:
        return (
            f"No relevant evidence was found in NovaCrop's knowledge base or PubMed for: "
            f"{question}"
            if question
            else "No relevant evidence was found in NovaCrop's knowledge base or PubMed."
        )

    if internal_empty:
        return (
            "No relevant NovaCrop internal evidence was found. "
            f"{state.get('external_summary') or 'External literature was retrieved but could not be summarized.'}"
        )

    return (
        "No relevant PubMed literature was found. "
        f"{state.get('internal_answer') or 'Internal evidence was retrieved but could not be summarized.'}"
    )


def synthesize_answer(state: GenomeBridgeState) -> dict:
    """Produce the final human-readable answer."""
    if not has_usable_evidence(state):
        return {"answer": _empty_answer(state)}

    question = state.get("question", "").strip()
    route = state.get("route", "internal")
    route_reason = state.get("route_reason", "")
    validation = state.get("validation")
    in_sync = state.get("in_sync")

    llm = build_llm()
    chain = SYNTHESIZE_ANSWER_PROMPT | llm
    response = chain.invoke(
        {
            "question": question,
            "route": route,
            "route_reason": route_reason,
            "internal_evidence": format_internal_evidence(state),
            "external_evidence": format_external_evidence(state),
            "validation": format_validation_result(validation),
            "in_sync": in_sync if in_sync is not None else "not assessed",
        }
    )

    return {"answer": response.content}
