from app.graphs.helpers.fetch_helpers import run_external_fetch, skipped_internal_fields
from app.graphs.state import GenomeBridgeState


async def fetch_external(state: GenomeBridgeState) -> dict:
    """Query external literature via MCP."""
    return {
        **await run_external_fetch(state),
        **skipped_internal_fields(),
    }
