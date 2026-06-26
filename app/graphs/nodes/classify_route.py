from langchain_openai import ChatOpenAI

from app.configs.config import Settings, get_settings
from app.graphs.prompts.classify_route import CLASSIFY_ROUTE_PROMPT
from app.graphs.schemas.route_classification import RouteClassification
from app.graphs.state import GenomeBridgeState, Route


def _build_classifier(settings: Settings | None = None) -> ChatOpenAI:
    settings = settings or get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.chat_model,
        temperature=0,
    )


def classify_route(state: GenomeBridgeState) -> dict:
    """Classify whether the question needs internal, external, or both sources."""
    question = state.get("question", "").strip()
    if not question:
        return {
            "route": "internal",
            "route_reason": "Empty question; defaulting to internal route.",
        }

    llm = _build_classifier().with_structured_output(RouteClassification)
    chain = CLASSIFY_ROUTE_PROMPT | llm
    result: RouteClassification = chain.invoke({"question": question})

    route: Route = result.route
    return {
        "route": route,
        "route_reason": result.reason,
    }
