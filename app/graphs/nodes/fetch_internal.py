from app.graphs.helpers.fetch_helpers import run_internal_fetch, skipped_external_fields
from app.graphs.state import GenomeBridgeState


def fetch_internal(state: GenomeBridgeState) -> dict:
    """Query NovaCrop internal knowledge base via RAG."""
    return {
        **run_internal_fetch(state),
        **skipped_external_fields(),
    }
