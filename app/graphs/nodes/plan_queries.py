from datetime import date

from langchain_openai import ChatOpenAI

from app.configs.config import Settings, get_settings
from app.graphs.prompts.plan_queries import PLAN_QUERIES_PROMPT
from app.graphs.schemas.query_plan import QueryPlan
from app.graphs.state import GenomeBridgeState, PlannedQueries, Route
from app.services.mcp.models import PubMedDateRange


def _current_year() -> int:
    return date.today().year


def _build_planner(settings: Settings | None = None) -> ChatOpenAI:
    settings = settings or get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.chat_model,
        temperature=0,
    )


def _build_date_range(plan: QueryPlan) -> PubMedDateRange | None:
    if not plan.external_min_date or not plan.external_max_date:
        return None

    return PubMedDateRange(
        min_date=plan.external_min_date.strip(),
        max_date=plan.external_max_date.strip(),
        date_type=plan.external_date_type,
    )


def _apply_route_constraints(plan: QueryPlan, route: Route) -> QueryPlan:
    if route == "internal":
        return plan.model_copy(
            update={
                "external_query": None,
                "external_min_date": None,
                "external_max_date": None,
            }
        )

    if route == "external":
        return plan.model_copy(update={"internal_query": None})

    return plan


def plan_queries(state: GenomeBridgeState) -> dict:
    """Rewrite the user question into internal and/or external search queries."""
    question = state.get("question", "").strip()
    route: Route = state.get("route", "internal")
    route_reason = state.get("route_reason", "")

    if not question:
        planned = PlannedQueries()
        return {
            "planned_queries": planned,
            "internal_query": None,
            "external_query": None,
            "external_date_range": None,
            "external_max_results": 5,
        }

    current_year = _current_year()
    llm = _build_planner().with_structured_output(QueryPlan)
    chain = PLAN_QUERIES_PROMPT | llm
    result: QueryPlan = chain.invoke(
        {
            "question": question,
            "route": route,
            "route_reason": route_reason,
            "current_year": current_year,
            "last_three_years_start": current_year - 3,
        }
    )

    result = _apply_route_constraints(result, route)
    date_range = _build_date_range(result)

    planned = PlannedQueries(
        internal_query=result.internal_query,
        external_query=result.external_query,
        external_date_range=date_range,
        external_max_results=result.external_max_results,
    )

    return {
        "planned_queries": planned,
        "internal_query": result.internal_query,
        "external_query": result.external_query,
        "external_date_range": date_range,
        "external_max_results": result.external_max_results,
    }
