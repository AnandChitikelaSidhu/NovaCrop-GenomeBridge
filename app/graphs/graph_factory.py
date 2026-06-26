from functools import lru_cache

from langgraph.graph.state import CompiledStateGraph

from app.graphs.genome_bridge_graph import build_genome_bridge_graph


@lru_cache
def get_genome_bridge_graph() -> CompiledStateGraph:
    return build_genome_bridge_graph()
