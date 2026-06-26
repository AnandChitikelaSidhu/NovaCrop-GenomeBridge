import asyncio

from app.graphs.helpers.fetch_helpers import run_external_fetch, run_internal_fetch
from app.graphs.state import GenomeBridgeState


async def fetch_both(state: GenomeBridgeState) -> dict:
    """Query RAG and MCP in parallel."""
    internal_result, external_result = await asyncio.gather(
        asyncio.to_thread(run_internal_fetch, state),
        run_external_fetch(state),
    )
    return {**internal_result, **external_result}
