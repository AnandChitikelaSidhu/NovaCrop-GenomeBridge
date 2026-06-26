from typing import Literal

from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    internal_query: str | None = Field(
        default=None,
        description="Search query for NovaCrop internal knowledge base. Null if route is external only.",
    )
    external_query: str | None = Field(
        default=None,
        description="PubMed search query. Null if route is internal only.",
    )
    external_min_date: str | None = Field(
        default=None,
        description="Publication start date for PubMed filter (YYYY, YYYY/MM, or YYYY/MM/DD).",
    )
    external_max_date: str | None = Field(
        default=None,
        description="Publication end date for PubMed filter (YYYY, YYYY/MM, or YYYY/MM/DD).",
    )
    external_date_type: Literal["pdat", "mdat", "edat"] = Field(
        default="pdat",
        description="PubMed date field for filtering. Use pdat unless the user specifies otherwise.",
    )
    external_max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum PubMed articles to retrieve.",
    )
    planning_notes: str = Field(
        description="Brief note on how the queries and dates were derived.",
    )
