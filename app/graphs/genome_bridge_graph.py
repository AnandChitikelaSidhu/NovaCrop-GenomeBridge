from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.graphs.nodes import (
    classify_route,
    fetch_both,
    fetch_external,
    fetch_internal,
    plan_queries,
    prepare_evidence,
    synthesize_answer,
    validate_sync,
)
from app.graphs.helpers.evidence_helpers import should_validate_sync
from app.graphs.state import GenomeBridgeState


def _route_after_plan(
    state: GenomeBridgeState,
) -> Literal["fetch_internal", "fetch_external", "fetch_both"]:
    route = state.get("route", "internal")
    if route == "external":
        return "fetch_external"
    if route == "both":
        return "fetch_both"
    return "fetch_internal"


def _should_validate_sync(
    state: GenomeBridgeState,
) -> Literal["validate_sync", "synthesize_answer"]:
    if should_validate_sync(state):
        return "validate_sync"
    return "synthesize_answer"


def build_genome_bridge_graph():
    graph = StateGraph(GenomeBridgeState)

    graph.add_node("classify_route", classify_route)
    graph.add_node("plan_queries", plan_queries)
    graph.add_node("fetch_internal", fetch_internal)
    graph.add_node("fetch_external", fetch_external)
    graph.add_node("fetch_both", fetch_both)
    graph.add_node("prepare_evidence", prepare_evidence)
    graph.add_node("validate_sync", validate_sync)
    graph.add_node("synthesize_answer", synthesize_answer)

    graph.add_edge(START, "classify_route")
    graph.add_edge("classify_route", "plan_queries")
    graph.add_conditional_edges(
        "plan_queries",
        _route_after_plan,
        {
            "fetch_internal": "fetch_internal",
            "fetch_external": "fetch_external",
            "fetch_both": "fetch_both",
        },
    )
    graph.add_edge("fetch_internal", "prepare_evidence")
    graph.add_edge("fetch_external", "prepare_evidence")
    graph.add_edge("fetch_both", "prepare_evidence")
    graph.add_conditional_edges(
        "prepare_evidence",
        _should_validate_sync,
        {
            "validate_sync": "validate_sync",
            "synthesize_answer": "synthesize_answer",
        },
    )
    graph.add_edge("validate_sync", "synthesize_answer")
    graph.add_edge("synthesize_answer", END)

    return graph.compile()
