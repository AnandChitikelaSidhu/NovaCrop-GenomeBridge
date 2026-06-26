from typing import Literal

from pydantic import BaseModel, Field


class RouteClassification(BaseModel):
    route: Literal["internal", "external", "both"] = Field(
        description="Which knowledge sources are required to answer the question.",
    )
    reason: str = Field(
        description="Brief explanation for why this route was chosen.",
    )
