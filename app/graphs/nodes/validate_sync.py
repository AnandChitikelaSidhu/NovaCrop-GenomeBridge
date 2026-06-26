from app.graphs.helpers.evidence_helpers import (
    build_llm,
    format_external_evidence,
    format_internal_evidence,
    to_validation_result,
)
from app.graphs.prompts.validate_sync import VALIDATE_SYNC_PROMPT
from app.graphs.schemas.validation_assessment import ValidationAssessment
from app.graphs.state import GenomeBridgeState


def validate_sync(state: GenomeBridgeState) -> dict:
    """Compare internal and external evidence when both are available."""
    question = state.get("question", "").strip()
    llm = build_llm().with_structured_output(ValidationAssessment)
    chain = VALIDATE_SYNC_PROMPT | llm
    assessment: ValidationAssessment = chain.invoke(
        {
            "question": question,
            "internal_evidence": format_internal_evidence(state),
            "external_evidence": format_external_evidence(state),
        }
    )

    return {
        "in_sync": assessment.in_sync,
        "validation": to_validation_result(assessment),
    }
