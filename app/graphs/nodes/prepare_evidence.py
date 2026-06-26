from app.graphs.helpers.evidence_helpers import should_validate_sync
from app.graphs.state import GenomeBridgeState


def prepare_evidence(state: GenomeBridgeState) -> dict:
    """Normalize evidence after fetch and clear validation when sync will not run."""
    update: dict = {}

    if state.get("internal_sources") is None:
        update["internal_sources"] = []
    if state.get("external_sources") is None:
        update["external_sources"] = []

    if not should_validate_sync(state):
        update["in_sync"] = None
        update["validation"] = None

    return update
